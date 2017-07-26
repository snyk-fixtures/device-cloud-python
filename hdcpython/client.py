"""
This module contains the Client class for user applications
"""

import json
import os
import uuid

from hdcpython import defs
from hdcpython.constants import DEFAULT_CONFIG_DIR
from hdcpython.constants import DEFAULT_CONFIG_FILE
from hdcpython.constants import DEFAULT_LOG_LEVEL
from hdcpython.constants import DEFAULT_LOOP_TIME
from hdcpython.constants import DEFAULT_MESSAGE_TIMEOUT
from hdcpython.constants import DEFAULT_THREAD_COUNT
from hdcpython.constants import STATUS_SUCCESS
from hdcpython.constants import WORK_PUBLISH
from hdcpython.handler import Handler


class Client(object):
    """
    This class is used by apps to connect to and communicate with the HDC Cloud
    """

    def __init__(self, app_id, kwargs=None):
        """
        Called on initialization

        Parameters:
          app_id                       ID of application that will be used to
                                       generate a key. Also used as part of
                                       default configuration file
                                       [APP_ID]-connect.cfg
          kwargs                       Optional dict to override any
                                       configuration values. These can also be
                                       overridden individually later.
        """

        # Setup Config
        self.config = defs.Config()
        self.config.app_id = app_id

        # Set config defaults
        self.config.config_dir = DEFAULT_CONFIG_DIR
        self.config.config_file = DEFAULT_CONFIG_FILE.format(app_id)
        self.config.log_level = DEFAULT_LOG_LEVEL
        self.config.loop_time = DEFAULT_LOOP_TIME
        self.config.message_timeout = DEFAULT_MESSAGE_TIMEOUT
        self.config.thread_count = DEFAULT_THREAD_COUNT
        self.cloud = defs.Config()
        self.proxy = defs.Config()

        # Override config defaults with any passed values
        if kwargs:
            self.config.update(kwargs)


    def initialize(self):
        """
        Finish client setup by reading config files using any config values
        already set, and initializing the client handler

        Returns:
          STATUS_SUCCESS               Always
        """

        # Read JSON from config file.
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
                                       parameters, user_data). The callback
                                       function must also return status_code, or
                                       (status_code, status_message)

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
                      timeout=0):
        """
        Download a file from the Cloud to the device (C2D)

        Parameters:
          file_name                    File in Cloud to download
          download_dest                Destination for downloaded file
          blocking                     Wait for file transfer to complete
                                       before returning. Otherwise return
                                       immediately.
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
                                             timeout)

    def file_upload(self, file_filter, blocking=False, timeout=0):
        """
        Upload a file from the device to the Cloud (D2C)

        Parameters:
          file_filter                  Absolute path for uploading files.
                                       Supports Unix style filename wildcards
                                       for uploading multiple files.
          blocking                     Wait for file transfer to complete
                                       before returning. Otherwise return
                                       immediately.
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

        return self.handler.request_upload(file_filter, blocking, timeout)

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

