"""
This module contains the Client class for user applications
"""

import json
import os
import uuid

from hdcpython import defs
from hdcpython.constants import DEFAULT_CONFIG_DIR
from hdcpython.constants import DEFAULT_CONFIG_FILE
from hdcpython.constants import DEFAULT_KEEP_ALIVE
from hdcpython.constants import DEFAULT_LOOP_TIME
from hdcpython.constants import DEFAULT_MESSAGE_TIMEOUT
from hdcpython.constants import DEFAULT_THREAD_COUNT
from hdcpython.constants import STATUS_SUCCESS
from hdcpython.constants import WORK_PUBLISH
from hdcpython.handler import Handler


class Client(object):
    """
    This class is used by apps to connect to and communicate with the HDC Cloud

    Logging Functions:
        critical(message)
        debug(message)
        error(message)
        info(message)
        log(log_level, message)
        warning(message)
    """

    def __init__(self, app_id, kwargs=None):
        """
        Start configuration of client. Configuration file location and name can
        be updated after this if necessary. MUST be followed by
        client.initialize() before anything else can be done.

        Parameters:
          app_id                       ID of application that will be used to
                                       generate a key. Also used as part of
                                       default configuration file
                                       {APP_ID}-connect.cfg. Maximum 27
                                       characters.
          kwargs                       Optional dict to override any
                                       configuration values. These can also be
                                       overridden individually later.
        """

        # Setup default config structure and file location
        self.config = defs.Config()
        default_config = {
            "app_id":app_id,
            "config_dir":DEFAULT_CONFIG_DIR,
            "config_file":DEFAULT_CONFIG_FILE.format(app_id),
            "cloud":{},
            "proxy":{}
        }
        self.config.update(default_config)

        # Override config defaults with any passed values
        if kwargs:
            self.config.update(kwargs)


    def initialize(self):
        """
        Finish client setup by reading config files using any config values
        already set, and initializing the client handler. This is required
        before connection can be attempted.

        Returns:
          STATUS_SUCCESS               Configuration completed successfully
          Exception                    Error in configuration
        """

        # Read JSON from config file. Does not overwrite any configuration set
        # in application.
        kwargs = {}
        config_path = os.path.join(self.config.config_dir,
                                   self.config.config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as config_file:
                    kwargs.update(json.load(config_file))
            except IOError as error:
                print ("Error parsing JSON from "
                       "{}".format(self.config.config_file))
                raise error
        else:
            print "Cannot find {}".format(self.config.config_file)
            raise IOError("Cannot find {}".format(self.config.config_file))
        self.config.update(kwargs, False)

        kwargs = {}
        # Check config directory for device_id. If it does not exist, generate a
        # uuid and write it to device_id.
        device_id_path = os.path.join(self.config.config_dir, "device_id")
        if os.path.exists(device_id_path):
            try:
                with open(device_id_path, "r") as id_file:
                    self.config.device_id = id_file.read()
            except:
                print "Failed to read device_id"
                raise IOError("Failed to read device_id")
        else:
            try:
                with open(device_id_path, "w") as id_file:
                    self.config.device_id = str(uuid.uuid4())
                    id_file.write(self.config.device_id)
            except:
                print "Failed to write device_id"
                raise IOError("Failed to write device_id")
        self.config.update(kwargs, False)

        # Check that all necessary configuration has been obtained
        if not self.config.cloud.token:
            print "Cloud token not set. Must be set in config"
            raise KeyError("Cloud token not set. Must be set in config")
        if not self.config.cloud.host:
            print "Cloud host addess not set. Must be set in config"
            raise KeyError("Cloud host address not set. Must be set in config")
        if not self.config.cloud.port:
            print "Cloud port not set. Must be set in config"
            raise KeyError("Cloud port not set. Must be set in config")

        # Generate key
        if self.config.app_id and self.config.device_id:
            self.config.key = "{}-{}".format(self.config.device_id,
                                             self.config.app_id)
        else:
            print "app_id or device_id not set. Required for key."
            raise KeyError("app_id or device_id not set. Required for key.")

        if len(self.config.key) > 64:
            print("Key exceeds 64 bytes. Please specify an app_id under {} "
                  "bytes in length".format(64-len(self.config.device_id)))
            raise KeyError("Key exceeds 64 bytes. Please specify an app_id "
                           "under {} bytes in length".format(
                               64-len(self.config.device_id)))

        # Final precedence config defaults
        config_defaults = {
            "keep_alive":DEFAULT_KEEP_ALIVE,
            "loop_time":DEFAULT_LOOP_TIME,
            "message_timeout":DEFAULT_MESSAGE_TIMEOUT,
            "thread_count":DEFAULT_THREAD_COUNT
        }
        self.config.update(config_defaults, False)

        # Initialize handler
        self.handler = Handler(self.config, self)

        # Access logger functions
        self.critical = self.handler.logger.critical
        self.debug = self.handler.logger.debug
        self.error = self.handler.logger.error
        self.info = self.handler.logger.info
        self.log = self.handler.logger.log
        self.warning = self.handler.logger.warning

        return STATUS_SUCCESS

    def action_progress_update(self, request_id, message):
        """
        Update message for an action request from the Cloud

        Parameters:
          request_id                   If action_request.request_id was
                                       retreived from an action callback, it can
                                       be used here
          message                      New message for Cloud request

        Returns:
          STATUS_SUCCESS               Sent progress update for action request
          STATUS_FAILURE               Failed to update progress of action
                                       request
        """

        return self.handler.action_progress_update(request_id, message)


    def action_deregister(self, action_name):
        """
        Dissociates a Cloud action action from any command or callback

        Parameters:
          action_name                  action to deregister

        Returns:
          STATUS_NOT_FOUND             No action with that name registered
          STATUS_SUCCESS               Action deregistered
        """

        return self.handler.action_deregister(action_name)

    def action_register_callback(self, action_name, callback_function,
                                 user_data=None):
        """
        Associate a callback function with an action in the Cloud

        Parameters:
          action_name                  action to register
          callback_function            function to execute when triggered by
                                       action. Callback function must take
                                       parameters of the form (client,
                                       parameters, user_data[, action_request])
                                       where action_request is optional, but
                                       contains the request_id for later use.
                                       The callback function must also return
                                       status_code, or (status_code,
                                       status_message) in a tuple.

        Returns:
          STATUS_EXISTS                Action with that name already exists
          STATUS_SUCCESS               Successfully registered callback
        """

        return self.handler.action_register_callback(action_name,
                                                     callback_function,
                                                     user_data)

    def action_register_command(self, action_name, command):
        """
        Associate a console command with an action in the Cloud

        Parameters:
          action_name                  action to register
          command                      console command to execute when
                                       triggered by action
        Returns:
          STATUS_EXISTS                Action with that name already exists
          STATUS_SUCCESS               Successfully registered command
        """

        return self.handler.action_register_command(action_name, command)

    def alarm_publish(self, alarm_name, state, message=None):
        """
        Publish an alarm to the Cloud

        Parameters:
          alarm_name                   name of alarm to publish
          state                        state of publish
          message                      optional message to accompany alarm

        Returns:
          STATUS_SUCCESS               Alarm has been queued for publishing
        """

        alarm = defs.PublishAlarm(alarm_name, state, message)
        self.handler.queue_publish(alarm)
        work = defs.Work(WORK_PUBLISH, None)
        return self.handler.queue_work(work)

    def attribute_publish(self, attribute_name, value):
        """
        Publish string telemetry to the Cloud

        Parameters:
          attribute_name               name of attribute to publish to
          value                        value to publish

        Returns:
          STATUS_SUCCESS               Attribute has been queued for publishing
        """

        attr = defs.PublishAttribute(attribute_name, value)
        return self.handler.queue_publish(attr)

    def connect(self, timeout=0):
        """
        Connect the Client to the Cloud

        Parameters:
          timeout                      maximum time to try to connect

        Returns:
          STATUS_FAILURE               Failed to connect to Cloud
          STATUS_SUCCESS               Successfully connected to Cloud
          STATUS_TIMED_OUT             Connection attempt timed out
        """

        return self.handler.connect(timeout)

    def disconnect(self, wait_for_replies=False, timeout=0):
        """
        End Client connection to the Cloud

        Parameters:
          wait_for_replies             When True, wait for any pending replies to
                                       be received or time out before
                                       disconnecting
          timeout                      Maximum time to wait before returning

        Returns:
          STATUS_SUCCESS               Successfully disconnected
        """

        return self.handler.disconnect(wait_for_replies=wait_for_replies,
                                       timeout=timeout)

    def event_publish(self, message):
        """
        Publishes an event message to the Cloud

        Parameters:
          message                      Message to publish

        Returns:
          STATUS_SUCCESS               Event has been queued for publishing
        """

        log = defs.PublishLog(message)
        return self.handler.queue_publish(log)

    def file_download(self, file_name, download_dest, blocking=False,
                      callback=None, timeout=0):
        """
        Download a file from the Cloud to the device (C2D)

        Parameters:
          file_name                    File in Cloud to download
          download_dest                Destination for downloaded file
          blocking                     Wait for file transfer to complete
                                       before returning. Otherwise return
                                       immediately.
          callback                     Function to be executed as soon as file
                                       transfer is complete. It will be passed
                                       (client, file_name, status).
          timeout                      If blocking, maximum time to wait
                                       before returning

        Returns:
          STATUS_FAILURE               Failed to download file.
          STATUS_NOT_FOUND             Could not find download directory to
                                       download file to.
          STATUS_SUCCESS               File download successful
          STATUS_TIMED_OUT             Wait for file transfer timed out. File
                                       transfer is still in progress.
        """

        return self.handler.request_download(file_name, download_dest, blocking,
                                             callback, timeout)

    def file_upload(self, file_path, upload_name=None, blocking=False,
                    callback=None, timeout=0):
        """
        Upload a file from the device to the Cloud (D2C)

        Parameters:
          file_path                    Absolute path for file to upload.
          upload_name                  Name for file uploaded in Cloud.
                                       Default is the file name on the device.
          blocking                     Wait for file transfer to complete
                                       before returning. Otherwise return
                                       immediately.
          callback                     Function to be executed as soon as file
                                       transfer is complete. It will be passed
                                       (client, file_name, status).
          timeout                      If blocking, maximum time to wait
                                       before returning

        Returns:
          STATUS_FAILURE               Failed to upload file.
          STATUS_NOT_FOUND             Could not find find to upload in upload
                                       directory.
          STATUS_SUCCESS               File upload successful
          STATUS_TIMED_OUT             Wait for file transfer timed out. File
                                       transfer is still in progress.
        """

        return self.handler.request_upload(file_path, upload_name, blocking,
                                           callback, timeout)

    def is_alive(self):
        """
        Return whether or not the Client has exited

        Returns:
          True                         Client is running
          False                        Client is not running
        """

        return not self.handler.to_quit

    def is_connected(self):
        """
        Return the current connect status of the Client

        Returns:
          True                         Connected to Cloud
          False                        Not connected to Cloud
        """

        return self.handler.is_connected()

    def location_publish(self, latitude, longitude, heading=None, altitude=None,
                         speed=None, accuracy=None, fix_type=None):
        """
        Publish a location metric to the Cloud

        Parameters:
          latitude                     latitude coordinate
          longitude                    longitude coordinate
          heading                      heading
          altitude                     altitude
          speed                        speed
          accuracy                     accuracy of fix
          fix_type                     fix type

        Returns:
          STATUS_SUCCESS               Location has been queued for publishing
        """

        location = defs.PublishLocation(latitude, longitude, heading=heading,
                                        altitude=altitude, speed=speed,
                                        accuracy=accuracy, fix_type=fix_type)
        return self.handler.queue_publish(location)

    def telemetry_publish(self, telemetry_name, value):
        """
        Publish telemetry to the Cloud

        Parameters:
          telemetry_name               name of property to publish to
          value                        value to publish

        Returns:
          STATUS_SUCCESS               Telemetry has been queued for publishing
        """

        telem = defs.PublishTelemetry(telemetry_name, value)
        return self.handler.queue_publish(telem)

