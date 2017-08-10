#!/usr/bin/env python

import json
import os
import unittest
from binascii import crc32
import mock
import re

from time import sleep

import hdcpython
import hdcpython_test.test_helpers as helpers


class ClientActionDeregister(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up Mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Set up a callback function
        user_data = "user data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)

        # Register action with callback
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

        # Deregister action
        result = self.client.action_deregister("action-name")
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionReregisterNotExist(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Attempt to deregister an action that does not exist
        result = self.client.action_deregister("action-name")
        assert result == hdcpython.STATUS_NOT_FOUND
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCallback(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Register action with callback
        user_data = "user data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCallbackExists(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Setup callbacks and user data
        user_data = "user data"
        user_data_2 = "user_data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)
        callback_2 = helpers.configure_callback_function(self.client, None,
                                                         user_data_2, 0)

        # Register action with callback
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

        # Attempt (and fail) to register same action with a different callback
        result = self.client.action_register_callback("action-name", callback_2,
                                                      user_data_2)
        assert result == hdcpython.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCommand(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Register action with a command
        command = "do a thing"
        result = self.client.action_register_command("action-name", command)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCommandExists(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Set up commands
        command = "do a thing"
        command_2 = "do a different thing"

        # Regsiter action with a command
        result = self.client.action_register_command("action-name", command)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

        # Attempt (and fail) to register action with a different command
        result = self.client.action_register_command("action-name", command_2)
        assert result == hdcpython.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientAlarmPublish(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue alarm for publishing
        result = self.client.alarm_publish("alarm_key", 5,
                                           message="alarm message")
        assert result == hdcpython.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, hdcpython.defs.PublishAlarm)
        assert pub.name == "alarm_key"
        assert pub.state == 5
        assert pub.message == "alarm message"
        work = self.client.handler.work_queue.get()
        assert work.type == hdcpython.constants.WORK_PUBLISH

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientAttributePublish(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue attribute for publishing
        result = self.client.attribute_publish("attribute_key",
                                               "attribute string")
        assert result == hdcpython.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, hdcpython.defs.PublishAttribute)
        assert pub.name == "attribute_key"
        assert pub.value == "attribute string"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientConnectFailure(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_mqtt.return_value.on_connect_rc = -1

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Fail to connect
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_FAILURE
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_alive() is False
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientConnectSuccess(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.client.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect successfully
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is True
        assert self.client.disconnect() == hdcpython.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientDisconnectFailure(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_mqtt.return_value.on_disconnect_rc = -1

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Receive failure for disconnecting
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_alive() is True
        assert self.client.is_connected() is True
        assert self.client.disconnect() == hdcpython.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_alive() is False
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientEventPublish(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue event (log) for publishing
        result = self.client.event_publish("event message")
        assert result == hdcpython.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, hdcpython.defs.PublishLog)
        assert pub.message == "event message"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientFileDownloadAsyncSuccess(unittest.TestCase):
    @mock.patch("hdcpython.handler.open")
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.handler.os.rename")
    @mock.patch("hdcpython.handler.os.path.isdir")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    @mock.patch("hdcpython.handler.requests.get")
    def runTest(self, mock_get, mock_mqtt, mock_sleep, mock_exists, mock_isdir, mock_rename, mock_client_open, mock_handle_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isdir.side_effect = [False, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_client_read = mock_client_open.return_value.__enter__.return_value.read
        mock_client_read.side_effect = read_strings
        mock_handle_write = mock_handle_open.return_value.__enter__.return_value.write
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_get.return_value.status_code = 200
        file_content = ["This ", "is ", "totally ", "a ", "file.\n",
                        "What ", "are ", "you ", "talking ", "about.\n"]
        mock_get.return_value.iter_content.return_value = file_content
        written_arr = []
        mock_handle_write.side_effect = written_arr.append
        download_callback = mock.Mock()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == hdcpython.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request download
        result = self.client.file_download("filename.ext",
                                           "/destination/file.ext",
                                           callback=download_callback)
        assert result == hdcpython.STATUS_SUCCESS
        download_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        assert args[2] == 1
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.get"
        assert jload["1"]["params"]["fileName"] == "filename.ext"

        # Set up and 'receive' reply from Cloud
        checksum = 0
        for content in file_content:
            checksum = crc32(content, checksum)
        checksum &= 0xffffffff
        message = mock.Mock()
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789",
                                                     "fileSize":4532,
                                                     "crc32":checksum}}})
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)
        #TODO Make a better check for download completion

        # Check to see what has been downloaded and written to a file
        written = "".join(filter(lambda x: x is not None, written_arr))
        assert written == "This is totally a file.\nWhat are you talking about.\n"
        args = download_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == hdcpython.STATUS_SUCCESS

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientFileUploadAsyncSuccess(unittest.TestCase):
    @mock.patch("hdcpython.handler.open")
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.handler.os.path.isfile")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    @mock.patch("hdcpython.handler.requests.post")
    def runTest(self, mock_post, mock_mqtt, mock_sleep, mock_exists, mock_isfile, mock_client_open, mock_handle_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_client_read = mock_client_open.return_value.__enter__.return_value.read
        mock_client_read.side_effect = read_strings
        file_content = "This is totally a file.\nWhat are you talking about.\n"
        mock_handle_open.return_value.__enter__.return_value = file_content
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        post_kwargs = {}
        def post_func(url, data=None, verify=None):
            post_kwargs["url"] = url
            post_kwargs["data"] = data
            post_kwargs["verify"] = verify
            return mock.Mock(status_code=200)
        mock_post.side_effect = post_func
        upload_callback = mock.Mock()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == hdcpython.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request upload
        result = self.client.file_upload("/path/to/some/filename.ext",
                                         callback=upload_callback)
        assert result == hdcpython.STATUS_SUCCESS
        checksum = 0
        checksum = crc32(file_content, checksum)
        checksum &= 0xffffffff
        upload_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        assert args[2] == 1
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.put"
        assert jload["1"]["params"]["fileName"] == "filename.ext"
        assert jload["1"]["params"]["crc32"] == checksum

        # Set up and 'receive' reply from Cloud
        message = mock.Mock()
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789"}}})
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)
        #TODO Make a better check for upload completion

        # Check to see what has been uploaded
        assert post_kwargs["url"] == "https://api.notarealcloudhost.com/file/123456789"
        assert post_kwargs["verify"] == "/top/secret/location"
        assert post_kwargs["data"] == "This is totally a file.\nWhat are you talking about.\n"
        args = upload_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == hdcpython.STATUS_SUCCESS

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientLocationPublish(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue location for publishing
        result = self.client.location_publish(12.34, 56.78, heading=90.12,
                                              altitude=34.56, speed=78.90,
                                              accuracy=12.34, fix_type="gps")
        assert result == hdcpython.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, hdcpython.defs.PublishLocation)
        assert pub.latitude == 12.34
        assert pub.longitude == 56.78
        assert pub.heading == 90.12
        assert pub.altitude == 34.56
        assert pub.speed == 78.90
        assert pub.accuracy == 12.34
        assert pub.fix_type == "gps"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientTelemetryPublish(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue telemetry for publishing
        result = self.client.telemetry_publish("property_key", 26.6)
        assert result == hdcpython.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, hdcpython.defs.PublishTelemetry)
        assert pub.name == "property_key"
        assert pub.value == 26.6

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ConfigReadFile(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        self.client.initialize()

        # Checkt that the 'file' was read and parsed correctly
        mock_open.assert_any_call("some/other/directory/device_id", "r")
        mock_open.assert_any_call("some/other/directory/someotherfile.cfg", "r")
        assert mock_read.call_count == 2
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.cloud.port == 8883
        assert self.client.config.cloud.token == "abcdefghijklm"
        assert self.client.config.ca_bundle_file == "/top/secret/location"
        assert self.client.config.validate_cloud_cert == True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ConfigReadDefaults(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, False]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_write = mock_open.return_value.__enter__.return_value.write

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # Check that all defaults are being used
        mock_open.assert_any_call("./testing-client-connect.cfg", "r")
        mock_open.assert_any_call("./device_id", "w")
        mock_read.assert_called()
        mock_write.assert_called()
        assert self.client.config.ca_bundle_file is None
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.cloud.port == 8883
        assert self.client.config.cloud.token == "abcdefghijklm"
        assert self.client.config.config_dir == "."
        assert self.client.config.config_file == "testing-client-connect.cfg"
        assert self.client.config.keep_alive == 300
        assert self.client.config.loop_time == 1
        assert self.client.config.thing_def_key is None
        assert self.client.config.thread_count == 3

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = {"cloud":{"host":"api.notarealcloudhost.com",
                           "port":8883, "token":"abcdefghijklm"}}

class ConfigWriteReadDeviceID(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, False]
        read_strings = [json.dumps(self.config_args)]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_write = mock_open.return_value.__enter__.return_value.write
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = hdcpython.Client("testing-client")
        self.client.initialize()

        # device_id is generated and written when the device_id file is not
        # found
        device_id = self.client.config.device_id
        mock_write.assert_called_once_with(device_id)
        mock_read.assert_called_once()
        mock_open.reset_mock()
        mock_read.reset_mock()
        mock_write.reset_mock()
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), device_id]
        mock_read.side_effect = read_strings

        # device_id is read and used when it exists
        self.client_2 = hdcpython.Client("testing-client-2")
        self.client_2.initialize()
        assert mock_read.call_count == 2
        assert mock_write.call_count == 0
        mock_write.asser_not_called()
        assert self.client_2.config.device_id == device_id

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class HandleActionExecCallbackSuccess(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.defs.inspect")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_inspect, mock_sleep, mock_exists,
                mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_inspect.getargspec.return_value.args.__len__.return_value = 3
        mock_inspect.ismethod.return_value = False
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Set up action callback
        mqtt = self.client.handler.mqtt
        params = {"some_param":521, "some_other_param":6234}
        user_data = "User Data"
        callback = mock.Mock(return_value=(0, "I did it!"))
        action = hdcpython.defs.Action("some_action", callback, self.client, user_data)
        self.client.handler.callbacks.add_action(action)

        # Connect to Cloud
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS

        thing_key = mock_mqtt.call_args_list[0][0][0]
        assert thing_key == "{}-testing-client".format(helpers.uuid)

        # Set up and 'receive' a notification from Cloud
        notify_payload = {"sessionId":"thisdoesntreallyneedtobehere",
                          "thingKey":thing_key}
        message_1 = mock.Mock()
        message_1.payload = json.dumps(notify_payload)
        message_1.topic = "notify/mailbox_activity"
        mqtt.messages.put(message_1)
        sleep(1)
        #TODO Make a better check for action handling

        # Published mailbox check
        mqtt.publish.assert_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        assert args[2] == 1
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "mailbox.check"
        callback.assert_not_called()

        # Set up and 'receive' reply from Cloud
        exec_payload = {"1":{"success":True,
                             "params":{"messages":[{"command":"method.exec",
                                                    "id":"impretendingtobeamailid",
                                                    "params":{"method":"some_action",
                                                              "thingDefKey":"testingthingdef",
                                                              "params":params},
                                                    "thingKey":thing_key}]}}}
        message_2 = mock.Mock()
        message_2.payload = json.dumps(exec_payload)
        message_2.topic = "reply/0001"
        mqtt.messages.put(message_2)
        sleep(1)
        #TODO Make a better check for action handling

        # Called callback
        callback.assert_called()
        args = callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == params
        assert args[2] is user_data

        # Published result of callback
        assert mqtt.publish.call_count == 2
        args = mqtt.publish.call_args_list[1][0]
        assert args[0] == "api/0002"
        assert args[2] == 1
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "mailbox.ack"
        assert jload["1"]["params"]["errorCode"] == 0
        assert jload["1"]["params"]["errorMessage"] == "I did it!"
        assert jload["1"]["params"]["id"] == "impretendingtobeamailid"
        assert len(self.client.handler.reply_tracker) == 1

        # Set up and 'receive' reply from Cloud
        ack_payload = {"1":{"success":True}}
        message_3 = mock.Mock()
        message_3.payload = json.dumps(ack_payload)
        message_3.topic = "reply/0002"
        mqtt.messages.put(message_3)
        sleep(1)
        #TODO Make a better check for action handling
        assert len(self.client.handler.reply_tracker) == 0

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class HandlePublishAllTypes(unittest.TestCase):
    @mock.patch("hdcpython.client.open")
    @mock.patch("hdcpython.client.os.path.exists")
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.initialize()

        # Set up pending publishes
        alarm = hdcpython.defs.PublishAlarm("alarm_key", 6,
                                            message="I'm an alarm")
        attr = hdcpython.defs.PublishAttribute("attribute_key",
                                               "Attribute String")
        loc = hdcpython.defs.PublishLocation(11.11, 22.22, heading=33.33,
                                             altitude=44.44, speed=55.55,
                                             accuracy=66.66, fix_type="gps")
        event = hdcpython.defs.PublishLog("Event Message")
        telem = hdcpython.defs.PublishTelemetry("property_key", 12.34)
        publishes = [alarm, attr, loc, event, telem]
        for pub in publishes:
            self.client.handler.queue_publish(pub)

        # Connect to Cloud
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS
        sleep(2)
        #TODO Make a better check for publish handling
        thing_key = mock_mqtt.call_args_list[0][0][0]
        assert thing_key == "{}-testing-client".format(helpers.uuid)
        mqtt = self.client.handler.mqtt

        # Published all in queue
        mqtt.publish.assert_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        assert args[2] == 1
        jload = json.loads(args[1])
        assert len(jload) == 5
        assert len(self.client.handler.reply_tracker) == 5
        assert jload["1"]["command"] == "alarm.publish"
        assert jload["1"]["params"]["thingKey"] == thing_key
        assert jload["1"]["params"]["state"] == 6
        assert jload["1"]["params"]["msg"] == "I'm an alarm"
        assert jload["2"]["command"] == "attribute.publish"
        assert jload["2"]["params"]["thingKey"] == thing_key
        assert jload["2"]["params"]["key"] == "attribute_key"
        assert jload["2"]["params"]["value"] == "Attribute String"
        assert jload["3"]["command"] == "location.publish"
        assert jload["3"]["params"]["thingKey"] == thing_key
        assert jload["3"]["params"]["lat"] == 11.11
        assert jload["3"]["params"]["lng"] == 22.22
        assert jload["3"]["params"]["heading"] == 33.33
        assert jload["3"]["params"]["altitude"] == 44.44
        assert jload["3"]["params"]["speed"] == 55.55
        assert jload["3"]["params"]["fixAcc"] == 66.66
        assert jload["3"]["params"]["fixType"] == "gps"
        assert jload["4"]["command"] == "log.publish"
        assert jload["4"]["params"]["thingKey"] == thing_key
        assert jload["4"]["params"]["msg"] == "Event Message"
        assert jload["5"]["command"] == "property.publish"
        assert jload["5"]["params"]["thingKey"] == thing_key
        assert jload["5"]["params"]["key"] == "property_key"
        assert jload["5"]["params"]["value"] == 12.34

        # Set up and 'receive' reply from Cloud
        ack_payload = {"1":{"success":True},
                       "2":{"success":True},
                       "3":{"success":True},
                       "4":{"success":True},
                       "5":{"success":True}}
        message = mock.Mock()
        message.payload = json.dumps(ack_payload)
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)
        #TODO Make a better check for publish handling
        assert len(self.client.handler.reply_tracker) == 0

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class OTAExecute(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = "echo 'Hello'"
        mock_system.return_value = 0

        self.ota = hdcpython.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == hdcpython.STATUS_SUCCESS
        mock_system.assert_called_once_with(test_cmd)

class OTAExecuteBadCommand(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = "eacho 'Hello'"
        mock_system.return_value = 127

        self.ota = hdcpython.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == hdcpython.STATUS_EXECUTION_ERROR
        mock_system.assert_called_once_with(test_cmd)

class OTAExecuteNoCommand(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = None
        mock_system.return_value = -1

        self.ota = hdcpython.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == hdcpython.STATUS_NOT_FOUND
        mock_system.assert_not_called()

class OTAExecuteBadWorkingDir(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        mock_system.return_value = 0
        mock_isdir.return_value = False
        test_cmd = "echo 'Hello'"

        self.ota = hdcpython.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd, ".....not_a_real_dir.....")

        assert result == hdcpython.STATUS_SUCCESS
        mock_system.assert_called_once_with(test_cmd)

class OTAExecuteWorkingDir(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        mock_system.return_value = 0
        mock_isdir.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler();
        result = self.ota._execute("echo 'Hello'", "../")

        full_cmd = mock_system.call_args[0][0]
        pat = re.compile("cd \\.\\.\\/(;|( &)) echo 'Hello'")
        assert pat.match(full_cmd) != None
        assert result == hdcpython.STATUS_SUCCESS
        mock_system.assert_called_once()

class OTAPackageDownload(unittest.TestCase):
    @mock.patch("hdcpython.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = hdcpython.STATUS_SUCCESS

        self.client = hdcpython.Client("testing-client")
        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(self.client, "fake.tar.gz")
        assert result == hdcpython.STATUS_SUCCESS

class OTAPackageDownloadNoClient(unittest.TestCase):
    @mock.patch("hdcpython.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = hdcpython.STATUS_SUCCESS

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(None, "fake.tar.gz")
        assert result == hdcpython.STATUS_BAD_PARAMETER

class OTAPackageDownloadBadFile(unittest.TestCase):
    @mock.patch("hdcpython.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = hdcpython.STATUS_FAILURE

        self.client = hdcpython.Client("testing-client")
        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(self.client, "fake.tar.gz")
        assert result == hdcpython.STATUS_FAILURE

class OTAPackageUnzipOther(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def runTest(self, mock_isfile):
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.rar", "bbbb")
        assert result == hdcpython.STATUS_NOT_SUPPORTED

class OTAPackageUnzipTar(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile.extractall")
    @mock.patch("tarfile.TarFile.close")
    def runTest(self, mock_close, mock_extract, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == hdcpython.STATUS_SUCCESS

class OTAPackageUnzipZip(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("zipfile.ZipFile")
    @mock.patch("zipfile.ZipFile.extractall")
    @mock.patch("zipfile.ZipFile.close")
    def runTest(self, mock_close, mock_extract, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.zip", "bbbb")
        assert result == hdcpython.STATUS_SUCCESS

class OTAPackageUnzipOpenException(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile")
    def runTest(self, mock_tar, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        mock_open.side_effect = IOError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == hdcpython.STATUS_FILE_OPEN_FAILED

        mock_open.side_effect = OSError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == hdcpython.STATUS_FILE_OPEN_FAILED

class OTAPackageUnzipExtractException(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile")
    def runTest(self, mock_tar, mock_open, mock_isfile):
        mock_isfile.return_value = True
        mock_open.return_value = mock_tar

        self.ota = hdcpython.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        mock_tar.extractall.side_effect = IOError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == hdcpython.STATUS_IO_ERROR

        mock_tar.extractall.side_effect = OSError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == hdcpython.STATUS_IO_ERROR

class OTAReadUpdateJSON(unittest.TestCase):
    @mock.patch("json.load")
    @mock.patch("os.path.isfile")
    @mock.patch("__builtin__.open")
    def runTest(self, mock_open, mock_isfile, mock_json):
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        result = self.ota._read_update_json("fake")
        assert result[0] == hdcpython.STATUS_SUCCESS
        assert result[1] != None

class OTAReadUpdateJSONBadFormat(unittest.TestCase):
    @mock.patch("json.load")
    @mock.patch("os.path.isfile")
    @mock.patch("__builtin__.open")
    def runTest(self, mock_open, mock_isfile, mock_json):
        mock_json.side_effect = ValueError
        mock_isfile.return_value = True

        self.ota = hdcpython.ota_handler.OTAHandler()
        result = self.ota._read_update_json("fake")
        assert result[0] == hdcpython.STATUS_IO_ERROR
        assert result[1] == None

class OTAReadUpdateJSONNonExistant(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def runTest(self, mock_isfile):
        mock_isfile.return_value = False

        self.ota = hdcpython.ota_handler.OTAHandler()
        result = self.ota._read_update_json("")
        assert result[0] == hdcpython.STATUS_BAD_PARAMETER
        assert result[1] == None

class OTAUpdateCallback(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("__builtin__.open")
    @mock.patch("threading.Thread.start")
    def runTest(self, mock_start, mock_open, mock_isfile):
        mock_isfile.return_value = False

        self.client = hdcpython.Client("testing-client")
        self.ota = hdcpython.ota_handler.OTAHandler()

        result = self.ota.update_callback(self.client, {}, ["aaaa"], None)
        assert result[0] == hdcpython.STATUS_INVOKED

class OTAUpdateCallbackInProgress(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("__builtin__.open")
    @mock.patch("threading.Thread.start")
    def runTest(self, mock_start, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.client = hdcpython.Client("testing-client")
        self.ota = hdcpython.ota_handler.OTAHandler()

        result = self.ota.update_callback(self.client, {}, ["aaaa"], None)
        assert result[0] == hdcpython.STATUS_FAILURE

class OTAUpdateSoftware(unittest.TestCase):
    """
    Test "suite" that will run success and failure cases on the main
    "_update_software" method.
    """
    @mock.patch("hdcpython.Client")
    def setUp(self, mock_client):
        self.ota = hdcpython.ota_handler.OTAHandler()
        self.client = hdcpython.Client("testing-client")
        self.params = {"package": "fake"}
        self.update_data = {"pre_install": "pre", \
                            "install": "install", \
                            "post_install": "post", \
                            "err_action": "err"}
        self.request = mock.Mock()
        self.request.message_id = 1234

    @mock.patch("os.remove")
    @mock.patch("os.path")
    @mock.patch("hdcpython.ota_handler.OTAHandler._execute")
    @mock.patch("hdcpython.ota_handler.OTAHandler._read_update_json")
    @mock.patch("hdcpython.ota_handler.OTAHandler._package_unzip")
    @mock.patch("hdcpython.ota_handler.OTAHandler._package_download")
    def runTest(self, mock_dl, mock_unzip, mock_read, mock_execute, mock_path, mock_remove):
        # Store mocks for tests
        self.mock_dl = mock_dl
        self.mock_unzip = mock_unzip
        self.mock_read = mock_read
        self.mock_execute = mock_execute
        self.mock_path = mock_path
        self.mock_remove = mock_remove

        # Run Tests
        self.successCase()
        self.downloadFailCase()
        self.unzipFailCase()
        self.dataReadFailCase()
        self.preInstallFailCase()
        self.installFailCase()
        self.postInstallFailCase()
        self.preInstallNoneCase()
        self.postInstallNoneCase()

    def resetMocks(self):
        self.mock_dl.reset_mock()
        self.mock_unzip.reset_mock()
        self.mock_read.reset_mock()
        self.mock_execute.reset_mock()
        self.mock_path.reset_mock()
        self.mock_remove.reset_mock()
        self.client.reset_mock()

        self.mock_execute.side_effect = None

        self.mock_path.isdir.return_value = False
        self.mock_path.isfile.return_value = False
        self.mock_dl.return_value = hdcpython.STATUS_SUCCESS
        self.mock_unzip.return_value = hdcpython.STATUS_SUCCESS
        self.mock_read.return_value = (hdcpython.STATUS_SUCCESS, self.update_data)
        self.mock_execute.return_value = hdcpython.STATUS_SUCCESS

    def successCase(self):
        self.resetMocks()

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") in self.client.log.call_args_list

    def downloadFailCase(self):
        self.resetMocks()
        self.mock_dl.return_value = hdcpython.STATUS_FAILURE

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_not_called()
        self.mock_read.assert_not_called()
        assert self.mock_execute.call_count == 0
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Download Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def unzipFailCase(self):
        self.resetMocks()
        self.mock_unzip.return_value = hdcpython.STATUS_IO_ERROR

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_not_called()
        assert self.mock_execute.call_count == 0
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Unzip Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def dataReadFailCase(self):
        self.resetMocks()
        self.mock_read.return_value = (hdcpython.STATUS_FAILURE, "")

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 0
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Data Read Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def preInstallFailCase(self):
        self.resetMocks()
        self.mock_execute.return_value = None
        self.mock_execute.side_effect = [hdcpython.STATUS_EXECUTION_ERROR, hdcpython.STATUS_SUCCESS, hdcpython.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 1
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Pre-Install Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def installFailCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [hdcpython.STATUS_SUCCESS, hdcpython.STATUS_EXECUTION_ERROR, hdcpython.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 2
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Install Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def postInstallFailCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [hdcpython.STATUS_SUCCESS, hdcpython.STATUS_SUCCESS, hdcpython.STATUS_EXECUTION_ERROR]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Post-Install Failed!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def preInstallNoneCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [hdcpython.STATUS_NOT_FOUND, hdcpython.STATUS_SUCCESS, hdcpython.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Pre-Install Failed!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list

    def postInstallNoneCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [hdcpython.STATUS_SUCCESS, hdcpython.STATUS_SUCCESS, hdcpython.STATUS_NOT_FOUND]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(hdcpython.LOGINFO, "OTA Successful!") in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "Post-Install Failed!") not in self.client.log.call_args_list
        assert mock.call(hdcpython.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list
