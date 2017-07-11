
import defs
import json
import os
import uuid

from constants import *
from datetime import datetime
from handler import Handler

class Client:
    """
    This class is used by apps to connect to and communicate with the HDC Cloud
    """

    def __init__(self, name, log_file=None, loop_time=None,
            message_timeout=None, thread_count=None):
        """
        Called on initialization.

        log_file                       optional file to print logs to as well as
                                       the console
        loop_time                      maximum time between each MQTT iteration
        message_timeout                maximum time a message can wait without a
                                       reply before timing out
        thread_count                   number of worker threads to spawn
        """

        # Collect all local arguments for later parsing
        kwargs = locals()

        # TODO: default path to config files ($CONFIG_DIR ?)
        # Read JSON from config files.
        if os.path.exists("iot.cfg"):
            try:
                with open("iot.cfg") as config_file:
                    kwargs.update(json.load(config_file))
            except Exception as e:
                print("Error parsing JSON from iot.cfg")
                raise e
        if os.path.exists("iot-connect.cfg"):
            try:
                with open("iot-connect.cfg") as config_file:
                    kwargs.update(json.load(config_file))
            except Exception as e:
                print("Error parsing JSON from iot-connect.cfg")
                raise e
        else:
            print("Cannot find iot-connect.cfg")
            raise Exception("Cannot find iot-connect.cfg")

        runtime_dir = kwargs.get("runtime_dir")
        if runtime_dir:
            # Check runtime directory for file transfer directories. If they do
            # not exist, create them.
            if not os.path.isdir(os.path.join(runtime_dir, "download")):
                try:
                    os.makedirs(os.path.join(runtime_dir, "download"))
                except:
                    print("Failed to make download directory")
                    raise Exception("Failed to make download directory")
            if not os.path.isdir(os.path.join(runtime_dir, "upload")):
                try:
                    os.makedirs(os.path.join(runtime_dir, "upload"))
                except:
                    print("Failed to make upload directory")
                    raise Exception("Failed to make upload directory")

            # Check runtime directory for deivce_id. If it does not exist,
            # generate a uuid and write it to device_id.
            if os.path.exists(os.path.join(runtime_dir, "device_id")):
                try:
                    with open(os.path.join(runtime_dir, "device_id"), "r") as file:
                        kwargs["device_id"] = file.read()
                except:
                    print("Failed to read device_id")
                    raise Exception("Failed to read device_id")
            else:
                try:
                    with open(os.path.join(runtime_dir, "device_id"), "w") as file:
                        kwargs["device_id"] = str(uuid.uuid4())
                        file.write(kwargs["device_id"])
                except:
                    print("Failed to write device_id")
                    raise Exception("Failed to write device_id")

        # Parse and store configuration for Client
        self.config = defs.Config(kwargs)

        # Check that all necessary configuration has been obtained
        if not self.config.cloud_token:
            print("Cloud token not set. Must be set in iot-connect.cfg")
            raise KeyError("Cloud token not set. Must be set in "
                    "iot-connect.cfg")
        if not self.config.cloud_host:
            self.logger.error("Cloud host addess not set. Must be set in "
                    "iot-connect.cfg")
            raise KeyError("Cloud host address not set. Must be set in "
                    "iot-connect.cfg")
        if not self.config.cloud_port:
            self.logger.error("Cloud port not set. Must be set in "
                    "iot-connect.cfg")
            raise KeyError("Cloud port not set. Must be set in "
                    "iot-connect.cfg")

        # Initialize handler
        self.handler = Handler(self.config, self)

        # Access logger functions
        self.log = self.handler.logger.info
        self.error = self.handler.logger.error

    def action_deregister(self, action_name):
        """
        Dissociates a Cloud action action from any command or callback

        action_name                    action to deregister
        """

        return self.handler.action_deregister_callback(action_name)

    def action_register_callback(self, action_name, callback_function,
            user_data=None):
        """
        Associate a callback function with an action in the Cloud

        action_name                    action to register
        callback_function              function to execute when
                                       triggered by action
        """

        return self.handler.action_register_callback(action_name,
                callback_function, user_data)

    def action_register_command(self, action_name, command):
        """
        Associate a console command with an action in the Cloud

        action_name                    action to register
        command                        console command to execute when
                                       triggered by action
        """

        return self.handler.action_register_command(action_name, command)

    def connect(self, timeout=0):
        """
        Connect the Client to the Cloud

        timeout                        maximum time to try to connect
        """

        return self.handler.connect(timeout)

    def disconnect(self, wait_for_replies=False, timeout=0):
        """
        End Client connection to the Cloud

        wait_for_replies               when set, wait for any pending replies to
                                       be received or time out before
                                       disconnecting
        timeout                        maximum time to wait before returning
        """

        return self.handler.disconnect(wait_for_replies=wait_for_replies,
                timeout=timeout)

    def file_download(self, file_name, blocking=False, timeout=0):
        """
        Download a file from the Cloud to the device (C2D)

        file_name                      file in Cloud to download
        blocking                       wait for file transfer to complete
                                       before returning
        timeout                        if blocking, maximum time to wait
                                       before returning
        """

        return self.handler.request_download(file_name, blocking, timeout)

    def file_upload(self, file_filter, blocking=False, timeout=0):
        """
        Upload a file from the device to the Cloud (D2C)

        file_filter                    any file in upload directory matching
                                       this pattern will be uploaded
        blocking                       wait for file transfer to complete
                                       before returning
        timeout                        if blocking, maximum time to wait
                                       before returning
        """

        return self.handler.request_upload(file_filter, blocking, timeout)

    def is_connected(self):
        """
        Return the current connect status of the Client
        """

        return self.handler.is_connected()

    def location_publish(self, latitude, longitude, heading=None, altitude=None,
            speed=None, accuracy=None, fix_type=None):
        """
        Publish a location metric to the Cloud

        latitude                       latitude coordinate
        longitude                      longitude coordinate
        heading                        heading
        altitude                       altitude
        speed                          speed
        accuracy                       accuracy of fix
        fix_type                       fix type
        """

        location = defs.Location(latitude, longitude, heading=heading,
                altitude=altitude, speed=speed, accuracy=accuracy,
                fix_type=fix_type)
        return self.telemetry_publish("location", location)

    def telemetry_publish(self, telemetry_name, value):
        """
        Publish telemetry to the Cloud

        telemetry_name                 name of property to publish to
        value                          value to publish
        """

        telem = defs.Telemetry(telemetry_name, value)
        return self.handler.queue_telemetry(telem)

    def attribute_publish(self, attribute_name, value):
        """
        Publish string telemetry to the Cloud

        telemetry_name                 name of attribute to publish to
        value                          value to publish
        """

        telem = defs.Telemetry(attribute_name, value)
        return self.handler.queue_telemetry(telem)

