
import defs
import fnmatch
import json
import logging
import os
import paho.mqtt.client as mqttlib
import Queue
import random
import requests
import ssl
import threading
import tr50
import traceback

from binascii import crc32
from constants import *
from constants import _STATUS_STRINGS
from constants import _WORK_MESSAGE
from constants import _WORK_PUBLISH
from constants import _WORK_ACTION
from constants import _WORK_DOWNLOAD
from constants import _WORK_UPLOAD
from datetime import datetime
from datetime import timedelta
from tr50 import TR50Command

from time import sleep



def error_string(error_code):
    """
    Return a string describing the error code
    """

    return _STATUS_STRINGS[error_code]


class Handler:
    """
    Handles all underlying functionality of the Client
    """

    def __init__(self, config, client):
        # Configuration
        self.config = config

        # Set Client
        self.client = client

        # Set up logging, with optional logging to a specified file
        if self.config.key:
            self.logger = logging.getLogger(self.config.key)
            self.event_logger = logging.getLogger(self.config.key + " events")
        else:
            self.logger = logging.getLogger("APP NAME HERE")
            self.event_logger = logging.getLogger("APP NAME HERE events")
        log_formatter = logging.Formatter("[%(asctime)s]%(levelname)s: "
                "%(filename)s:%(lineno)d (%(funcName)s) - %(message)s")
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(log_formatter)
        self.logger.addHandler(log_handler)
        if self.config.log_file:
            log_file_handler = logging.FileHandler(self.config.log_file)
            log_file_handler.setFormatter(log_formatter)
            self.logger.addHandler(log_file_handler)
        self.logger.setLevel(logging.DEBUG)

        # Ensure we're not missing required configuration information
        if not self.config.key or not self.config.cloud_token:
            self.logger.error("Missing key or cloud token from configuration")
            raise KeyError("Missing key or cloud token from configuration")

        # Print configuration
        for key in self.config:
            self.logger.debug("Config: %s %s", key, self.config[key])

        # Set up MQTT client
        self.mqtt = mqttlib.Client(self.config.key)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt.on_message = self.on_message
        self.mqtt.username_pw_set(self.config.key, self.config.cloud_token)

        # Dict to associate action names with callback functions and any user
        # data
        self.callbacks = defs.Callbacks()

        # Connection state of the Client
        self.state = STATE_DISCONNECTED

        # Lock for thread safety
        self.lock = threading.Lock()

        # Queue for any pending publishes (number, string, location, etc.)
        self.publish_queue = Queue.Queue()

        # Dicts to track which messages sent out have not received replies. Also
        # stores any actions to be taken when the reply is received.
        self.reply_tracker = defs.OutTracker()
        self.no_reply = []

        # Counter to allow every message to be sent on a unique topic
        self.topic_counter = 1

        # Thread trackers. Main thread for handling MQTT loop, and worker
        # threads for everything else.
        self.main_thread = None
        self.worker_threads = []

        # Queue to track any pending work (parsing messages, actions,
        # publishing, file transfer, etc.)
        self.work_queue = Queue.Queue()

    def action_deregister(self, action_name):
        """
        Disassociate any function or command from an action in the Cloud
        """

        status = STATUS_SUCCESS

        try:
            self.callbacks.remove_action(action_name)
        except KeyError as e:
            self.logger.error(str(e))
            status = STATUS_NOT_FOUND

        return status


    def action_register_callback(self, action_name, callback_function,
            user_data=None):
        """
        Associate a callback function with an action in the Cloud
        """

        status = STATUS_SUCCESS
        action = defs.Action(action_name, callback_function, self.client,
                user_data=user_data)
        try:
            self.callbacks.add_action(action)
            self.logger.info("Registered action \"%s\" with function \"%s\"",
                    action_name, callback_function.__name__)
        except KeyError as e:
            self.logger.error("Failed to register action. %s", str(e))
            status = STATUS_EXISTS

        return status

    def action_register_command(self, action_name, command):
        """
        Associate a console command with an action in the Cloud
        """

        status = STATUS_SUCCESS
        action = defs.ActionCommand(action_name, command, self.client)
        try:
            self.callbacks.add_action(action)
            self.logger.info("Registered action \"%s\" with command \"%s\"",
                    action_name, command)
        except KeyError as e:
            self.logger.error("Failed to register action. %s", str(e))
            status = STATUS_EXISTS

        return status

    def connect(self, timeout=0):
        """
        Connect to MQTT and start main thread
        """

        status = STATUS_FAILURE

        # Ensure we have a host and port to connect to
        if not self.config.cloud_host or not self.config.cloud_port:
            self.logger.error("Missing host or port from configuration")
            raise KeyError("Missing host or port from configuration")

        current_time = datetime.utcnow()
        end_time = current_time + timedelta(seconds=timeout)
        self.state = STATE_CONNECTING

        # Start a secure connection if the cert file is available
        if self.config.ca_bundle_file:
            self.mqtt.tls_set(self.config.ca_bundle_file,
                    tls_version=ssl.PROTOCOL_TLSv1_2)

        # Start MQTT connection
        result = self.mqtt.connect(self.config.cloud_host, self.config.cloud_port, 60)

        if result == 0:
            # Successful MQTT connection
            self.logger.info("Connecting...")
            #self.logger.info("Connecting... %s", mqtt.error_string(result))

            # Start main loop thread so that MQTT can make the on_connect
            # callback
            self.main_thread = threading.Thread(target=self.main_loop)
            self.main_thread.start()

            # Wait for cloud connection
            while ((timeout == 0 or current_time < end_time) and
                    self.state == STATE_CONNECTING):
                sleep(1)
                current_time = datetime.utcnow()

            # Still connecting, timed out
            if self.state == STATE_CONNECTING:
                self.logger.error("Connection timed out")
                state = STATUS_TIMED_OUT

        if self.state == STATE_CONNECTED:
            # Connected Successfully
            status = STATUS_SUCCESS
        else:
            # Not connected. Stop main loop.
            self.logger.error("Failed to connect")
            self.state = STATE_DISCONNECTED
            self.main_thread.join()

        # Return result of connection
        return status

    def disconnect(self, wait_for_replies=False, timeout=0):
        """
        Stop threads and shut down MQTT client
        """

        current_time = datetime.utcnow()
        end_time = current_time + timedelta(seconds=timeout)

        # Optionally wait for any outstanding replies. Any that timeout will be
        # removed so that this loop can end.
        if wait_for_replies:
            self.logger.info("Waiting for replies...")
            while ((timeout == 0 or current_time < end_time) and
                    not len( self.reply_tracker ) == 0):
                sleep(1)
                current_time = datetime.utcnow()

        # Disconnect MQTT and wait for main thread, which in turn waits for
        # worker threads
        self.logger.info("Disconnecting...")
        self.mqtt.disconnect()
        while ((timeout == 0 or current_time < end_time) and
                self.state == STATE_CONNECTED):
            sleep( 1 )
            current_time = datetime.utcnow()

        # Wait for pending work that has not been dealt with
        while ((timeout == 0 or current_time < end_time) and
                not self.work_queue.empty()):
            sleep(1)
            current_time = datetime.utcnow()

        self.state = STATE_DISCONNECTED
        self.main_thread.join()

        return STATUS_SUCCESS

    def handle_action(self, action_request):
        """
        Handle action execution requests from Cloud
        """

        try:
            # Execute callback
            result = self.callbacks.execute_action(action_request)

            # Handle returning a tuple or just a status code
            if result.__class__.__name__ == "tuple":
                result_code = result[0]
                if len(result) == 2:
                    result_message = result[1]
                else:
                    result_message = list(result[1:])
            else:
                result_code = result
                result_message = None

        except KeyError as e:
            # Action has not been registered
            self.logger.error(str(e))
            result_code = STATUS_NOT_FOUND
            result_message = "Unhandled action"

        # Return status to Cloud
        # TODO: return changed parameters
        mailbox_ack = tr50.create_mailbox_ack(action_request.id,
                errorCode=tr50.translate_error_code(result_code),
                errorMessage=result_message)
        message_description = "Action Complete \"{}\" result : {}".format(
                action_request.name, result_code)
        if result_message:
            message_description += " \"{}\"".format(result_message)
        message = defs.OutMessage(mailbox_ack, message_description)
        status = self.send(message)

        return status

    def handle_file_download(self, download):
        """
        Handle any accepted C2D file transfers
        """

        status = STATUS_SUCCESS
	self.logger.info("Downloading \"%s\"", download.fileName)

	# Start creating URL for file download
        URL = "{}/file/{}".format(self.config.cloud_host, download.fileId)

        # Download directory
        download_dir = os.path.join(self.config.runtime_dir, "download")
        # Temporary file name while downloading
        temp_path = os.path.join(download_dir, "{}.part".format(
                "".join([random.choice("0123456789") for x in range(10)])))
	# Path where temporary file will be moved to
        real_path = os.path.join(download_dir, download.fileName)

        # Ensure download directory exists
        if not os.path.isdir(download_dir):
            self.logger.error("Cannot find download directory \"%s\". "
                    "Download cancelled.", download_dir)
            status = STATUS_NOT_FOUND

        if status == STATUS_SUCCESS:
            # Secure or insecure HTTP request.
            response = None
            if self.config.ca_bundle_file:
                URL = "https://" + URL
                response = requests.get(URL, stream=True,
                        verify=self.config.ca_bundle_file)
            else:
                URL = "http://" + URL
                response = requests.get(URL, stream=True)

            if response.status_code == 200:
                # Write to temporary file
                with open(temp_path, "wb") as file:
                    for chunk in response.iter_content(512):
                        file.write(chunk)
                status = STATUS_SUCCESS
            else:
                # Request was unsuccessful
                self.logger.error("Failed to download \"%s\" (download error)",
                        download.fileName)
                self.logger.error(".... %s", response.content)
                status = STATUS_FAILURE

            if status == STATUS_SUCCESS:
                # Ensure the downloaded file matches the checksum sent by the
                # Cloud.
                checksum = 0
                with open(temp_path, "rb") as file:
                    for chunk in file:
                        checksum = crc32(chunk, checksum)
                    checksum = checksum & 0xffffffff
                if checksum == download.fileChecksum:
                    # Checksums match, move temporary file to real file position
                    os.rename(temp_path, real_path)
                    self.logger.info("Successfully downloaded \"%s\"",
                            download.fileName)
                else:
                    # Checksums do not match, remove temporary file and fail
                    os.remove(temp_path)
                    self.logger.error("Failed to download \"%s\" "
                            "(checksums do not match)", download.fileName)
                    status = STATUS_FAILURE

            # Update file transfer status
            download.status = status

        return status

    def handle_file_upload(self, upload):
        """
        Handle any accepted D2C file transfers
        """

        status = STATUS_SUCCESS

        self.logger.info("Uploading \"%s\"", upload.fileName)

        # Start creating URL for file upload
        URL = "{}/file/{}".format(self.config.cloud_host, upload.fileId)

        # Upload directory
        upload_dir = os.path.join(self.config.runtime_dir, "upload")
        # Path of file to upload
        file_path = os.path.join(upload_dir, upload.fileName)

        # Ensure upload directory exists
        if not os.path.isdir(upload_dir):
            self.logger.error("Cannot find upload directory \"%s\". "
                    "Upload cancelled.", upload_dir)
            status = STATUS_NOT_FOUND

        if status == STATUS_SUCCESS:
            # If file exists attempt upload
            response = None
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    # Secure or insecure HTTP Post
                    if self.config.ca_bundle_file:
                        URL = "https://" + URL
                        response = requests.post(URL, data=file,
                                verify=self.config.ca_bundle_file)
                    else:
                        URL = "http://" + URL
                        response = requests.post( URL, data=file )
                if response.status_code == 200:
                    self.logger.info("Successfully uploaded \"%s\"",
                            upload.fileName)
                    status = STATUS_SUCCESS
                else:
                    self.logger.error("Failed to upload \"%s\"",
                            upload.fileName)
                    self.logger.debug(".... %s", response.content)

            else:
                # File does not exist
                self.logger.error("File \"%s\" does not exist, cannot upload",
                        upload.fileName)
                status = STATUS_NOT_FOUND

            # Update file transfer status
            upload.status = status

        return status

    def handle_message(self, mqtt_message):
        """
        Handle messages received from Cloud
        """

        status = STATUS_NOT_SUPPORTED

        msg_json = mqtt_message.json
        if "notify/" in mqtt_message.topic:
            # Received a notification
            if mqtt_message.topic[len("notify/"):] == "mailbox_activity":
                # Mailbox activity, send a request to check the mailbox
                self.logger.info("Recevied notification of mailbox activity")
                mailbox_check = tr50.create_mailbox_check(autoComplete=False)
                to_send = defs.OutMessage(mailbox_check, "Mailbox Check")
                self.send(to_send)
                status = STATUS_SUCCESS

        elif "reply/" in mqtt_message.topic:
            # Received a reply to a previous message
            topic_num = mqtt_message.topic[len("reply/"):]
            for command_num in msg_json:
                reply = msg_json[command_num]

                # Retrieve the sent message that this is a reply for, removing
                # it from being tracked
                self.lock.acquire()
                try:
                    sent_message = self.reply_tracker.pop_message(topic_num,
                            command_num)
                except KeyError as e:
                    raise e
                finally:
                    self.lock.release()
                sent_command_type = sent_message.command.get("command")

                # Log success status of reply
                if reply.get("success"):
                    self.logger.info("Received success for %s-%s - %s",
                            topic_num, command_num, sent_message)
                else:
                    self.logger.error("Received failure for %s-%s - %s",
                            topic_num, command_num, sent_message)
                    self.logger.error(".... %s", str(reply))

                # Check what kind of message this is a reply to
                if sent_command_type == TR50Command.file_get:
                    # Recevied a reply for a file download request
                    if reply.get("success"):
                        fileId = reply["params"].get("fileId")
                        fileChecksum = reply["params"].get("crc32")
                        file_transfer = sent_message.data
                        file_transfer.fileId = fileId
                        file_transfer.fileChecksum = fileChecksum
                        work = defs.Work(_WORK_DOWNLOAD, file_transfer)
                        self.queue_work(work)
                    else:
                        sent_message.data.status = STATUS_FAILURE

                elif sent_command_type == TR50Command.file_put:
                    # Received a reply for a file upload request
                    if reply.get("success"):
                        fileId = reply["params"].get("fileId")
                        file_transfer = sent_message.data
                        file_transfer.fileId = fileId
                        work = defs.Work(_WORK_UPLOAD, file_transfer)
                        self.queue_work(work)
                    else:
                        sent_message.data.status = STATUS_FAILURE

                elif sent_command_type == TR50Command.mailbox_check:
                    # Received a reply for a mailbox check
                    if reply.get("success"):
                        for mail in reply["params"]["messages"]:
                            mail_command = mail.get("command")
                            if mail_command == "method.exec":
                                # Action execute request in mailbox
                                mail_id = mail.get("id")
                                action_name = mail["params"].get(
                                        "method")
                                action_params = mail["params"].get(
                                        "params")
                                action_request = defs.ActionRequest(
                                        mail_id, action_name,
                                        action_params)
                                work = defs.Work(_WORK_ACTION,
                                        action_request)
                                self.queue_work(work)

            status = STATUS_SUCCESS

        return status

    def handle_publish(self):
        """
        Publish any pending publishes in the publish queue, or the cloud logger
        """

        status = STATUS_SUCCESS

        # Collect all pending publishes in publish queue
        to_publish = []
        while not self.publish_queue.empty():
            try:
                to_publish.append(self.publish_queue.get())
            except Queue.Empty:
                break

        if to_publish:
            # If pending publishes are found, parse into list for sending
            messages = []
            for pub in to_publish:

                # Create publish command for strings
                if pub.type == "PublishAttribute":
                    command = tr50.create_attribute_publish(self.config.key,
                            pub.name, pub.value, ts=pub.ts)
                    message = defs.OutMessage(command, "Attribute Publish {} : "
                            "\"{}\"".format(pub.name, pub.value))

                # Create publish command for numbers
                elif pub.type == "PublishTelemetry":
                    command = tr50.create_property_publish(self.config.key,
                            pub.name, pub.value, ts=pub.ts)
                    message = defs.OutMessage(command, "Property Publish {} : "
                            "{}".format(pub.name, pub.value))

                # Create publish command for location
                elif pub.type == "PublishLocation":
                    command = tr50.create_location_publish(self.config.key,
                            pub.latitude, pub.longitude,
                            heading=pub.heading,
                            altitude=pub.altitude,
                            speed=pub.speed,
                            fixAcc=pub.accuracy,
                            fixType=pub.fix_type, ts=pub.ts)
                    message = defs.OutMessage(command,"Location Publish "
                            "{}".format(str(pub)))

                # Create publish command for a log
                elif pub.type == "PublishLog":
                    command = tr50.create_log_publish(self.config.key,
                            pub.message, ts=pub.ts)
                    message = defs.OutMessage(command, "Log Publish "
                            "{}".format(pub.message))

                messages.append(message)

            # Send all publishes
            status = self.send(messages)
        return status

    def handle_work_loop(self):
        """
        Loop for worker threads to handle any items put on the work queue
        """

        # Continuously loop while connected
        while self.is_connected():
            work = None
            try:
                work = self.work_queue.get(timeout=self.config.loop_time)
            except Queue.Empty:
                pass
            # If work is retrieved from the queue, handle it based on type
            if work:
                try:
                    if work.type == _WORK_MESSAGE:
                        self.handle_message(work.data)
                    elif work.type == _WORK_PUBLISH:
                        self.handle_publish()
                    elif work.type == _WORK_ACTION:
                        self.handle_action(work.data)
                    elif work.type == _WORK_DOWNLOAD:
                        self.handle_file_download(work.data)
                    elif work.type == _WORK_UPLOAD:
                        self.handle_file_upload(work.data)
                except Exception as e:
                    # Print traceback, but don't kill thread
                    print(traceback.format_exc())

        return STATUS_SUCCESS

    def is_connected(self):
        """
        Returns connection status of Client to Cloud
        """

        return self.state == STATE_CONNECTED

    def main_loop(self):
        """
        Main loop for MQTT to send and receive messages, as well as queue work
        for publishing and checking timeouts
        """

        # Continuously loop while connected or connecting
        while (self.state == STATE_CONNECTED or
                self.state == STATE_CONNECTING):
            self.mqtt.loop(timeout=self.config.loop_time)
            current_time = datetime.utcnow()
            to_remove = []

            self.lock.acquire()
            try:
                # Check if any messages have timed out with no reply
                removed = self.reply_tracker.time_out(current_time,
                        self.config.message_timeout)

                # Log any timed out messages
                if len(removed) > 0:
                    self.logger.error("Message(s) timed out:")
                for remove in removed:
                    self.logger.error(".... %s", remove.description)
            finally:
                self.lock.release()

            # Make a work item to publish anything that's pending
            if not self.publish_queue.empty():
                work = defs.Work(_WORK_PUBLISH, None)
                self.work_queue.put(work)

        # On disconnect, show all timed out messages
        if self.no_reply:
            self.logger.error("These messages never received a reply:")
            for nr in self.no_reply:
                self.logger.error(".... %s - %s", nr.id, nr.description)

        return STATUS_SUCCESS

    def on_connect(self, mqtt, userdata, flags, rc):
        """
        Callback when MQTT Client connects to Cloud
        """

        # Check connection result from MQTT
        self.logger.info("MQTT connected: %s", mqttlib.connack_string(rc))
        if rc == 0:
            self.state = STATE_CONNECTED
        else:
            self.state = STATE_DISCONNECTED

        # Start worker threads if we have successfully connected
        if self.state == STATE_CONNECTED:
            for i in range(self.config.thread_count):
                self.worker_threads.append(
                        threading.Thread(target=self.handle_work_loop))
            for thread in self.worker_threads:
                thread.start()

    def on_disconnect(self, mqtt, userdata, rc):
        """
        Callback when MQTT Client disconnects from Cloud
        """

        self.logger.info("MQTT disconnected %d", rc)
        self.state = STATE_DISCONNECTED
        # Wait for worker threads to finish.
        for thread in self.worker_threads:
            thread.join()

    def on_message(self, mqtt, userdata, msg):
        """
        Callback when MQTT Client receives a message
        """

        self.logger.debug("Received message on topic \"%s\"", msg.topic)
        self.logger.debug(".... %s", msg.payload)

        # Queue work to handle received message. Don't block main loop with this
        # task.
        message = defs.Message(msg.topic, json.loads(msg.payload))
        work = defs.Work(_WORK_MESSAGE, message)
        self.queue_work(work)

    def queue_publish(self, pub):
        """
        Place pub in the publish queue
        """

        self.publish_queue.put(pub)
        return STATUS_SUCCESS

    def queue_work(self, work):
        """
        Place work in the work queue
        """

        self.work_queue.put(work)
        return STATUS_SUCCESS

    def request_download(self, file_name, blocking=False, timeout=0):
        """
        Request a C2D file transfer
        """

        current_time = datetime.utcnow()
        end_time = current_time + timedelta(seconds=timeout)

        self.logger.info("Request download of %s", file_name)

        # File Transfer object for tracking progress
        transfer = defs.FileTransfer(file_name)

        # Generate and send message to request file transfer
        command = tr50.create_file_get(self.config.key, file_name)
        message = defs.OutMessage(command, "Download {}".format(file_name),
                data=transfer)
        status = self.send(message)

        # If blocking is set, wait for result of file transfer
        if status == STATUS_SUCCESS and blocking:
            while ((timeout == 0 or current_time < end_time) and
                    transfer.status == None):
                sleep(1)
                current_time = datetime.utcnow()

            if transfer.status == None:
                status = STATUS_TIMED_OUT
            else:
                status = transfer.status

        return status

    def request_upload(self, file_filter, blocking=False, timeout=0):
        """
        Request a D2C file transfer
        """

        status = STATUS_SUCCESS
        current_time = datetime.utcnow()
        end_time = current_time + timedelta(seconds=timeout)
        transfer = None

        self.logger.info("Request upload of %s", file_filter)

        # Check to make sure upload directory exists
        upload_dir = os.path.join(self.config.runtime_dir, "upload")
        if os.path.isdir(upload_dir):

            # Get a list of all matching files to upload
            files = [f for f in os.listdir(upload_dir) if
                    os.path.isfile(os.path.join(upload_dir, f))]
            files = fnmatch.filter(files, file_filter)
            #files = [os.path.join(upload_dir, f) for f in files]

            transfers = []
            for file_name in files:
                # Get file crc32 checksum
                checksum = 0
                with open(os.path.join(upload_dir, file_name), "rb") as file:
                    for chunk in file:
                        checksum = crc32(chunk, checksum)
                    checksum = checksum & 0xffffffff

                if checksum != 0:
                    # File Transfer object for tracking progress
                    transfer = defs.FileTransfer(file_name)

                    # Generate and send message to request file transfer
                    command = tr50.create_file_put(self.config.key, file_name)
                    message = defs.OutMessage(command,
                            "Upload {}".format(file_name), data=transfer)
                    status = self.send(message)
                    transfers.append(transfer)
                else:
                    self.logger.error("Upload request failed. Failed to "
                            "retrieve checksum for \"%s\".", file_name)
                    status = STATUS_FAILURE
                    break

        else:
            # Upload directory not found
            self.logger.error("Cannot find upload directory \"%s\". "
                    "Upload cancelled.", upload_dir)
            status = STATUS_NOT_FOUND

        # If blocking is set, wait for result of file transfer
        if transfers and status == STATUS_SUCCESS and blocking:
            while ((timeout == 0 or current_time < end_time) and
                    len(transfers) != 0) and self.is_connected():
                if transfers[0].status != None:
                    transfers.pop(0)
                else:
                    sleep(1)
                current_time = datetime.utcnow()

            if len(transfers) != 0:
                status = STATUS_TIMED_OUT
            else:
                status = STATUS_SUCCESS

        return status

    def send(self, messages):
        """
        Send commands to the Cloud, and track them to wait for replies
        """

        status = STATUS_FAILURE

        message_list = messages
        if messages.__class__.__name__ != "list":
            message_list = [messages]

        # Generate final request string
        payload = tr50.generate_request([x.command for x in message_list])

        # Lock to ensure all outgoing messages are tracked before handling
        # received messages
        self.lock.acquire()
        try:
            # Obtain new unused topic number
            while True:
                topic_num = "{:0>4}".format(self.topic_counter)
                self.topic_counter += 1
                if topic_num not in self.reply_tracker:
                    break

            # Send payload over MQTT
            result, mid = self.mqtt.publish("api/{}".format(topic_num),
                    payload, 1)

            if result == 0:
                status = STATUS_SUCCESS

                # Track outgoing messages
                current_time = datetime.utcnow()

                # Track each message
                for i in range(len(message_list)):

                    # Add timestamps and ids
                    message_list[i].ts = current_time
                    message_list[i].id = "{}-{}".format(topic_num, i+1)

                    self.reply_tracker.add_message(message_list[i])
                    self.logger.info("Sending %s-%d - %s", topic_num, i+1,
                            message_list[i])
                    self.logger.debug(".... %s", message_list[i].command)
        finally:
            self.lock.release()

        return status






