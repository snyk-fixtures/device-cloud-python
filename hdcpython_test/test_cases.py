#!/usr/bin/env python

import json
import os
import unittest
from binascii import crc32
import mock

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
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
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
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
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
        assert self.client.is_connected() is True
        assert self.client.disconnect() == hdcpython.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

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
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
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
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
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
        assert self.client.config.loop_time == 5
        assert self.client.config.message_timeout == 15
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
