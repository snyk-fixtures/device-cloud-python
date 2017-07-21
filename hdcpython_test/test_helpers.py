#!/usr/bin/env python

import json
import os
import shutil
import ssl
import mock


cwd = os.getcwd()

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

def config_files_default(runtime="runtime"):
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
    kwargs["runtime_dir"] = runtime
    kwargs["log_level"] = "INFO"
    return kwargs

def make_config_files(config_dir, kwargs):
    """
    Write configuration files
    """

    config_path = os.path.join(config_dir, "iot.cfg")
    connect_path = os.path.join(config_dir, "iot-connect.cfg")

    connect = {}
    config = {}

    connect["cloud"] = kwargs.get("cloud")
    connect["validate_cloud_cert"] = kwargs.get("validate_cloud_cert")
    connect["ca_bundle_file"] = kwargs.get("ca_bundle_file")
    connect["proxy"] = kwargs.get("proxy")
    for key, value in connect.items():
        if value is None:
            del connect[key]
    with open(connect_path, "w+") as connect_file:
        json.dump(connect, connect_file, sort_keys=True, indent=4,
                  separators=(",", ":"))

    config["runtime_dir"] = kwargs.get("runtime_dir")
    config["log_level"] = kwargs.get("log_level")
    config["actions_enabled"] = kwargs.get("actions_enabled")
    config["upload_remove_on_success"] = kwargs.get("upload_remove_on_success")
    config["upload_additional_dirs"] = kwargs.get("upload_additional_dirs")
    for key, value in config.items():
        if value is None:
            del config[key]
    with open(config_path, "w+") as config_file:
        json.dump(config, config_file, sort_keys=True, indent=4,
                  separators=(",", ":"))

def configure_init_mock_mqtt(connect_succeed=True, disconnect_succeed=True):
    """
    Configure pretend initializer for the specific test being performed
    """

    def init_mock_mqtt(client_id="", clean_session=True, userdata=None):
        """
        Pretend initializer for a mock MQTT client object
        """

        mock_mqtt = mock.Mock()
        mock_mqtt.on_connect = None
        mock_mqtt.on_disconnect = None
        mock_mqtt.on_message = None
        mock_mqtt.do_on_connect = False
        mock_mqtt.do_on_disconnect = False
        mock_mqtt.do_on_message = False
        mock_mqtt.do_message = ""

        def mqtt_tls_set(ca_certs, certfile=None, keyfile=None,
                         cert_reqs=ssl.CERT_REQUIRED,
                         tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None):
            return 0

        def mqtt_connect(host, port=1883, keepalive=60, bind_address=""):
            mock_mqtt.do_on_connect = True
            return 0

        def mqtt_disconnect():
            mock_mqtt.do_on_disconnect = True
            return 0

        def mqtt_loop(timeout=1.0, max_packets=1):
            if mock_mqtt.do_on_connect:
                rc = 0 if connect_succeed else -1
                mock_mqtt.on_connect(mock_mqtt, None, None, rc)
                mock_mqtt.do_on_connect = False
            elif mock_mqtt.do_on_disconnect:
                rc = 0 if disconnect_succeed else -1
                mock_mqtt.on_disconnect(None, None, rc)
                mock_mqtt.do_on_disconnect = False
            elif mock_mqtt.do_on_message:
                mock_mqtt.on_message(mock_mqtt, None, mock_mqtt.do_message)
                mock_mqtt.do_on_message = False
            return 0

        def mqtt_publish(topic, payload=None, qos=0, retain=False):
            return (0, 0)

        def mqtt_username_pw_set(username, password=None):
            return 0

        mock_mqtt.tls_set.side_effect = mqtt_tls_set
        mock_mqtt.connect.side_effect = mqtt_connect
        mock_mqtt.disconnect.side_effect = mqtt_disconnect
        mock_mqtt.loop.side_effect = mqtt_loop
        mock_mqtt.publish.side_effect = mqtt_publish
        mock_mqtt.username_pw_set.side_effect = mqtt_username_pw_set

        return mock_mqtt

    # Return generated function to generate a Mock in place of the MQTT object
    return init_mock_mqtt


def setup_func(case_dir):
    """
    Setup each test case to run in a different directory
    """

    path = os.path.join(cwd, "testruns", case_dir)
    config_path = os.path.join(path, "config")
    runtime_path = os.path.join(path, "runtime")
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    os.makedirs(config_path)
    os.environ["CONFIG_DIR"] = config_path
    os.makedirs(runtime_path)

    return path
