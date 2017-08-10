#!/usr/bin/env python

"""
Wind River Helix Device Cloud Python-based Device Manager. This module provides
multiple device management methods and attributes that allow for management of
a connected device.
"""

from collections import namedtuple
import errno
import json
import os
from os.path import abspath
import platform
import signal
import sys
from time import sleep

import hdcosal as osal
import hdcpython as iot

running = True

def sighandler(signum, frame):
    """
    Signal handler for exiting app.
    """
    global running
    print "Received signal {}, stopping application...".format(signum)
    running = False

def ack_messages(client, path):
    """
    Check for a pending message to acknowledge and, if present, send the mailbox
    acknowledgement to the cloud.
    """
    if os.path.isfile(path):
        with open(path, 'r') as id_file:
            msg_id = id_file.read()
            if msg_id:
                result_args = {"mail_id":msg_id}
                mailbox_ack = iot.tr50.create_mailbox_ack(**result_args)
                message = iot.defs.OutMessage(mailbox_ack, "Restart Complete")
                client.handler.send(message)

        os.remove(path)


def action_register_conditional(client, name, callback, enabled, \
                                user_data=None):
    """
    Register an action with the HDC client if it is enabled, otherwise register
    it using a generic "not implemented" callback.
    """
    return client.action_register_callback(name, callback \
            if enabled else method_not_implemented, user_data)

def agent_reset(client, params, user_data, request):
    """
    Callback function for the "reset_agent" method. Will stop and restart the
    device manager app.
    """
    global running
    running = False

    path = os.path.join(user_data[0], "message_ids")
    with open(path, 'w') as id_file:
        id_file.write(request.request_id)

    user_data[1].join()
    client.disconnect(wait_for_replies=True)
    os.execl("device_manager.py", "")

    # If this return is hit, then the device manager did not restart properly
    return (iot.STATUS_FAILURE, "Device Manager Failed to Restart!")

def config_load(cfg_dir=".", cfg_name="iot.cfg"):
    """
    Open and read configuration information from iot.cfg
    """
    config_data = None
    try:
        with open(os.path.join(cfg_dir, cfg_name), 'r') as cfg_file:
            config_data = json.load(cfg_file, \
                object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except IOError as error:
        print "Error parsing JSON from iot.cfg"
        print error

    return config_data

def device_decommission(client, params, user_data):
    """
    Callback for the "decommission_device" method that will remove HDC config
    files, preventing the device from reconnecting to the cloud. The device
    manager app will then shut down.
    """
    global running

    files_to_remove = [
        "iot.cfg",
        "iot-connect.cfg",
        "device_id"
        ]

    directories_to_remove = [
        os.path.join(user_data[0], "upload"),
        os.path.join(user_data[0], "download"),
        user_data[0]
        ]

    client.log(iot.LOGINFO, "Decommissioning Device!")

    for f in files_to_remove:
        try:
            os.remove(f)
        except OSError:
            client.log(iot.LOGWARNING, "Failed to remove {}".format(f))

    for directory in directories_to_remove:
        try:
            os.rmdir(directory)
        except OSError:
            client.log(iot.LOGWARNING, "Failed to remove {}".format(directory))

    client.log(iot.LOGINFO, "Device decommissioned! Stopping device manager.")
    running = False

    return (iot.STATUS_SUCCESS, "")

def device_reboot():
    """
    Callback for the "reboot_device" method which reboots the system.
    """
    retval = osal.system_reboot()

    if retval == 0:
        status = iot.STATUS_SUCCESS
        message = ""
    elif retval == osal.NOT_SUPPORTED:
        status = iot.STATUS_NOT_SUPPORTED
        message = "Reboot not supported on this platform!"
    else:
        status = iot.STATUS_FAILURE
        message = "Reboot failed with return code: " + str(retval)

    return (status, message)

def device_shutdown():
    """
    Callback for the "reboot_device" method which shuts-down the system.
    """
    retval = osal.system_shutdown()

    if retval == 0:
        status = iot.STATUS_SUCCESS
        message = ""
    elif retval == osal.NOT_SUPPORTED:
        status = iot.STATUS_NOT_SUPPORTED
        message = "Shutdown not supported on this platform!"
    else:
        status = iot.STATUS_FAILURE
        message = "Shutdown failed with return code: " + str(retval)

    return (status, message)


def file_download(client, params, user_data):
    """
    Callback for the "file_download" method which downloads a file from the
    cloud to the local system.
    """
    file_name = None
    file_dest = None
    result = None
    if params:
        file_name = params.get("file_name")
        file_dest = params.get("file_dest")
        if not file_dest:
            file_dest = abspath(os.path.join(user_data[0], "download"))

        file_global = params.get("global", False)

    if file_name:
        if not file_dest.startswith('~'):
            if not file_dest.startswith('/'):
                file_dest = abspath(os.path.join(user_data[0], file_dest))

            try:
                if not os.path.isdir(file_dest):
                    os.makedirs(file_dest)
            except (OSError, IOError) as e:
                result = iot.STATUS_IO_ERROR
                message = ("Destination directory does not exist and could not "
                           "be created!")
                client.log(iot.LOGERROR, message)
                print e

            if result == None:
                client.log(iot.LOGINFO, "Downloading")
                result = client.file_download(file_name, file_dest, \
                                              blocking=True, timeout=15, \
                                              file_global=file_global)
                if result == iot.STATUS_SUCCESS:
                    message = ""
                else:
                    message = iot.status_string(result)

        else:
            message = "Paths cannot use '~' to reference a home directory"
            result = iot.STATUS_BAD_PARAMETER
    else:
        result = iot.STATUS_BAD_PARAMETER
        message = "No file name and/or destination given"

    return (result, message)


def file_upload(client, params, user_data):
    """
    Callback for the "file_upload" method which uploads a file from the
    cloud to the local system. Wildcards in the file name are supported.
    """
    file_name = None
    if params:
        file_name = params.get("file_name")
        if "dest_name" in params:
            dest_name = params.get("dest_name")
        else:
            dest_name = None

        file_global = params.get("global", False)

    if file_name:
        if not file_name.startswith('~'):
            if not file_name.startswith('/'):
                file_name = abspath(os.path.join(user_data[0], "upload", \
                                    file_name))
            client.log(iot.LOGINFO, "Uploading {}".format(file_name))
            result = client.file_upload(file_name, upload_name=dest_name, \
                                        blocking=True, timeout=240, \
                                        file_global=file_global)
            if result == iot.STATUS_SUCCESS:
                message = ""
                if user_data[1] and file_name.startswith(user_data[0]):
                    os.remove(file_name)
            else:
                message = iot.status_string(result)
        else:
            message = "Paths cannot use '~' to reference a home directory"
            result = iot.STATUS_BAD_PARAMETER
    else:
        result = iot.STATUS_BAD_PARAMETER
        message = "No file name given"

    return (result, message)

def method_not_implemented():
    """
    Callback for disabled methods that simply tells the cloud that the requested
    method is not enabled for this device
    """
    return (iot.STATUS_NOT_SUPPORTED, \
            "This method is disabled by its iot.cfg setting")

def quit_me():
    """
    Callback for the "quit" method which exits the device manager app.
    """
    global running
    running = False
    return (iot.STATUS_SUCCESS, "")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler)
    if osal.LINUX:
        signal.signal(signal.SIGQUIT, sighandler)

    # Initialize client called 'device_manager_py'
    client = iot.Client("device_manager_py")
    client.config.config_file = "iot-connect.cfg"
    client.initialize()

    config = config_load()
    runtime_dir = config.runtime_dir

    upload_dir = os.path.join(runtime_dir, "upload")
    download_dir = os.path.join(runtime_dir, "download")

    try:
        if not os.path.isdir(runtime_dir):
            os.mkdir(runtime_dir)

        if not os.path.isdir(upload_dir):
            os.mkdir(upload_dir)

        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

    except (OSError, IOError) as e:
        print e
        client.log(iot.LOGERROR, ("Could not create one or more runtime "
                                  "directories! Did you run the device manager "
                                  "with sufficient priviliges?"))


    # Setup an OTA Handler
    ota = iot.ota.OTAHandler()

    # Set action callbacks, if enabled in iot.cfg
    action_register_conditional(client, "file_download", file_download, \
                                config.actions_enabled.file_transfers, \
                                (runtime_dir,))
    action_register_conditional(client, "file_upload", file_upload, \
                                config.actions_enabled.file_transfers, \
                                (runtime_dir, config.upload_remove_on_success))

    action_register_conditional(client, "shutdown_device", device_shutdown, \
                                config.actions_enabled.shutdown_device)

    action_register_conditional(client, "reboot_device", device_reboot, \
                                config.actions_enabled.reboot_device)

    action_register_conditional(client, "decommission_device", \
                                device_decommission, \
                                config.actions_enabled.decommission_device, \
                                (runtime_dir,))

    action_register_conditional(client, "software_update", \
                                ota.update_callback, \
                                config.actions_enabled.software_update,
                                (runtime_dir,))

    action_register_conditional(client, "reset_agent", agent_reset, \
                                config.actions_enabled.reset_agent, \
                                (runtime_dir, ota))
    action_register_conditional(client, "quit", quit_me, \
                                config.actions_enabled.reset_agent)

    # Connect to Cloud
    if client.connect(timeout=10) != iot.STATUS_SUCCESS:
        client.error("Failed")
        sys.exit(1)

    ack_messages(client, os.path.join(runtime_dir, "message_ids"))

    # Publish system details
    client.log(iot.LOGINFO, "Publishing platform: " + sys.platform)
    pstring = "{} {}".format(platform.system(), platform.release())
    client.attribute_publish("platform", pstring)
    client.attribute_publish("architecture", platform.machine())
    client.attribute_publish("hostname", platform.node())

    while running and client.is_alive():
        # Wrap sleep with an exception handler to fix SIGINT handling on Windows
        try:
            sleep(1)
        except IOError as err:
            if err.errno != errno.EINTR:
                raise

    # Wait for any OTA operations to finish
    if ota.is_running():
        client.log(iot.LOGINFO, "Waiting for OTA to finish...")
        ota.join()

    client.disconnect(wait_for_replies=True)

