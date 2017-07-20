"""
This module contains the Client class for user applications
"""

import json
import os
import uuid

from hdcpython import defs
from hdcpython.handler import Handler


class Client(object):
    """
    This class is used by apps to connect to and communicate with the HDC Cloud
    """

    def __init__(self, name, log_file=None, loop_time=None,
                 message_timeout=None, thread_count=None):
        """
        Called on initialization.

        Parameters:
          log_file                     optional file to print logs to as well as
                                       the console
          loop_time                    maximum time between each MQTT iteration
          message_timeout              maximum time a message can wait without a
                                       reply before timing out
          thread_count                 number of worker threads to spawn
        """

        # Collect all local arguments for later parsing
        kwargs = {}
        kwargs["name"] = name
        kwargs["log_file"] = log_file
        kwargs["loop_time"] = loop_time
        kwargs["message_timeout"] = message_timeout
        kwargs["thread_count"] = thread_count

        # TODO: default path to config files ($CONFIG_DIR ?)
        # Read JSON from config files.
        if os.path.exists("iot.cfg"):
            try:
                with open("iot.cfg", "r") as config_file:
                    kwargs.update(json.load(config_file))
            except Exception as error:
                print "Error parsing JSON from iot.cfg"
                raise error
        if os.path.exists("iot-connect.cfg"):
            try:
                with open("iot-connect.cfg", "r") as config_file:
                    kwargs.update(json.load(config_file))
            except Exception as error:
                print "Error parsing JSON from iot-connect.cfg"
                raise error
        else:
            print "Cannot find iot-connect.cfg"
            raise Exception("Cannot find iot-connect.cfg")

        runtime_dir = kwargs.get("runtime_dir")
        if runtime_dir:
            # Check runtime directory for file transfer directories. If they do
            # not exist, create them.
            if not os.path.isdir(os.path.join(runtime_dir, "download")):
                try:
                    os.makedirs(os.path.join(runtime_dir, "download"))
                except:
                    print "Failed to make download directory"
                    raise Exception("Failed to make download directory")
            if not os.path.isdir(os.path.join(runtime_dir, "upload")):
                try:
                    os.makedirs(os.path.join(runtime_dir, "upload"))
                except:
                    print "Failed to make upload directory"
                    raise Exception("Failed to make upload directory")

            # Check runtime directory for deivce_id. If it does not exist,
            # generate a uuid and write it to device_id.
            device_id_path = os.path.join(runtime_dir, "device_id")
            if os.path.exists(device_id_path):
                try:
                    with open(device_id_path, "r") as id_file:
                        kwargs["device_id"] = id_file.read()
                except:
                    print "Failed to read device_id"
                    raise Exception("Failed to read device_id")
            else:
                try:
                    with open(device_id_path, "w") as id_file:
                        kwargs["device_id"] = str(uuid.uuid4())
                        id_file.write(kwargs["device_id"])
                except:
                    print "Failed to write device_id"
                    raise Exception("Failed to write device_id")

        # Parse and store configuration for Client
        self.config = defs.Config(kwargs)

        # Check that all necessary configuration has been obtained
        if not self.config.cloud_token:
            print "Cloud token not set. Must be set in iot-connect.cfg"
            raise KeyError("Cloud token not set. Must be set in "
                           "iot-connect.cfg")
        if not self.config.cloud_host:
            print "Cloud host addess not set. Must be set in iot-connect.cfg"
            raise KeyError("Cloud host address not set. Must be set in "
                           "iot-connect.cfg")
        if not self.config.cloud_port:
            print "Cloud port not set. Must be set in iot-connect.cfg"
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
                                       (status_code, status_message), or
                                       (status_code, status_message,
                                       out_parameters).

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
        return self.handler.queue_publish(alarm)

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

    def file_download(self, file_name, blocking=False, timeout=0):
        """
        Download a file from the Cloud to the device (C2D)

        Parameters:
          file_name                    File in Cloud to download
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

        return self.handler.request_download(file_name, blocking, timeout)

    def file_upload(self, file_filter, blocking=False, timeout=0):
        """
        Upload a file from the device to the Cloud (D2C)

        Parameters:
          file_filter                  any file in upload directory matching
                                       this pattern will be uploaded
          blocking                     wait for file transfer to complete
                                       before returning. Otherwise return
                                       immediately.
          timeout                      if blocking, maximum time to wait
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

