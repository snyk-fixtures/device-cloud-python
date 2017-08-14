#!/usr/bin/env python

import ssl
from Queue import Queue
from time import sleep
import mock


uuid = "991d72fb-03b6-471d-8d0e-8134beaae7a2"

def configure_callback_function(expected_client, expected_params,
                                expected_user_data, return_tuple):
    """
    Configure a generic callback function and what it should expect if it is
    executed
    """

    def callback_function(client, params, user_data):
        assert client is expected_client
        assert user_data is expected_user_data
        #TODO compare all params
        return return_tuple
    return callback_function

def config_file_default():
    """
    Default configuration to allow unrelated tests to run
    """

    kwargs = {}
    kwargs["cloud"] = {}
    kwargs["cloud"]["host"] = "api.notarealcloudhost.com"
    kwargs["cloud"]["port"] = 8883
    kwargs["cloud"]["token"] = "abcdefghijklm"
    kwargs["validate_cloud_cert"] = "true"
    kwargs["ca_bundle_file"] = "/top/secret/location"
    return kwargs


def init_mock_mqtt():
    """
    Pretend initializer for a mock MQTT client object
    """

    mock_mqtt = mock.Mock()
    mock_mqtt.on_connect = None
    mock_mqtt.on_connect_exec = False
    mock_mqtt.on_disconnect = None
    mock_mqtt.on_message = None
    mock_mqtt.on_connect_rc = 0
    mock_mqtt.on_disconnect_rc = 0
    mock_mqtt.messages = Queue()

    def mqtt_connect(host, port=1883, keepalive=60, bind_address=""):
        mock_mqtt.on_connect_exec = True
        return 0

    def mqtt_disconnect():
        if mock_mqtt.on_disconnect:
            mock_mqtt.on_disconnect(None, None, mock_mqtt.on_disconnect_rc)
        return 0

    def mqtt_loop(timeout=1.0, max_packets=1):
        if mock_mqtt.on_connect_exec:
            mock_mqtt.on_connect(mock_mqtt, None, None,
                                 mock_mqtt.on_connect_rc)
            mock_mqtt.on_connect_exec = False
        elif not mock_mqtt.messages.empty():
            mock_mqtt.on_message(mock_mqtt, None, mock_mqtt.messages.get())
        else:
            sleep(0.25)
        return 0

    mock_mqtt.tls_set.return_value = 0
    mock_mqtt.connect.side_effect = mqtt_connect
    mock_mqtt.disconnect.side_effect = mqtt_disconnect
    mock_mqtt.loop.side_effect = mqtt_loop
    mock_mqtt.publish.return_value = (0, 0)
    mock_mqtt.username_pw_set.return_value = 0

    return mock_mqtt

