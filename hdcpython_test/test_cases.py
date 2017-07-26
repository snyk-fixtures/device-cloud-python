#!/usr/bin/env python

import os
import unittest
import mock

import hdcpython
import hdcpython_test.test_helpers as helpers


class ClientActionDeregister(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
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
        result = self.client.action_deregister("action-name")
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        self.test_path = helpers.setup_func("ClientActionDeregister")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientActionReregisterNotExist(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        result = self.client.action_deregister("action-name")
        assert result == hdcpython.STATUS_NOT_FOUND
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        self.test_path = helpers.setup_func("ClientActionReregisterNotExist")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientActionRegisterCallback(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
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
        self.test_path = helpers.setup_func("ClientActionRegisterCallback")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientActionRegisterCallbackExists(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        user_data = "user data"
        user_data_2 = "user_data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)
        callback_2 = helpers.configure_callback_function(self.client, None,
                                                         user_data_2, 0)
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)
        result = self.client.action_register_callback("action-name", callback_2,
                                                      user_data_2)
        assert result == hdcpython.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

    def setUp(self):
        self.test_path = helpers.setup_func("ClientActionRegisterCallbackExists")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientActionRegisterCommand(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        command = "do a thing"
        result = self.client.action_register_command("action-name", command)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        self.test_path = helpers.setup_func("ClientActionRegisterCommand")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientActionRegisterCommandExists(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        command = "do a thing"
        command_2 = "do a different thing"
        result = self.client.action_register_command("action-name", command)
        assert result == hdcpython.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command
        result = self.client.action_register_command("action-name", command_2)
        assert result == hdcpython.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        self.test_path = helpers.setup_func("ClientActionRegisterCommandExists")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ClientConnectFailure(unittest.TestCase):
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client",
                side_effect=helpers.configure_init_mock_mqtt(False, True))
    def runTest(self, mock_sleep, mock_mqtt):
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_FAILURE
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is False

    def setUp(self):
        self.test_path = helpers.setup_func("ClientConnectFailure")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

    def tearDown(self):
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientConnectSuccess(unittest.TestCase):
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client",
                side_effect=helpers.configure_init_mock_mqtt(True, True))
    def runTest(self, mock_sleep, mock_mqtt):
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is True
        assert self.client.disconnect() == hdcpython.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        self.test_path = helpers.setup_func("ClientConnectSuccess")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

    def tearDown(self):
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientDisconnectFailure(unittest.TestCase):
    @mock.patch("hdcpython.handler.sleep")
    @mock.patch("hdcpython.handler.mqttlib.Client",
                side_effect=helpers.configure_init_mock_mqtt(True, False))
    def runTest(self, mock_sleep, mock_mqtt):
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = hdcpython.Client("testing-client", kwargs)
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == hdcpython.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is True
        assert self.client.disconnect() == hdcpython.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        self.test_path = helpers.setup_func("ClientDisconnectFailure")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

    def tearDown(self):
        self.client.handler.state = hdcpython.constants.STATE_DISCONNECTED
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ConfigReadFile(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.ca_bundle_file == "/top/secret/location"

    def setUp(self):
        self.test_path = helpers.setup_func("ConfigReadFile")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)

class ConfigReadDefaults(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.ca_bundle_file is None

    def setUp(self):
        self.test_path = helpers.setup_func("ConfigReadDefaults")
        kwargs = {"cloud":{"host":"api.notarealcloudhost.com",
                           "port":8883, "token":"abcdefghijklm"}}
        helpers.make_config_file(self.test_path, kwargs)

class ConfigReadDeviceID(unittest.TestCase):
    def runTest(self):
        self.client = hdcpython.Client("testing-client")
        self.client.config.config_dir = self.test_path
        self.client.initialize()
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.ca_bundle_file == "/top/secret/location"
        dev_id = self.client.config.device_id
        self.client_2 = hdcpython.Client("testing-client-2")
        self.client_2.config.config_dir = self.test_path
        self.client_2.initialize()
        assert self.client_2.config.device_id == dev_id

    def setUp(self):
        self.test_path = helpers.setup_func("ConfigReadDeviceID")
        kwargs = helpers.config_file_default()
        helpers.make_config_file(self.test_path, kwargs)
        kwargs["config_file"] = "testing-client-2-connect.cfg"
        helpers.make_config_file(self.test_path, kwargs)
