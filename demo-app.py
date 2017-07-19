#!/usr/bin/env python

import hdcpython as iot
import math
import os
import random
import signal
import sys

from time import sleep

running = True
sending_telemetry = False
sending_location = False

# Second intervals between telemetry
TELEMINTERVAL = 4

# Initial location data.
heading = random.uniform(0, 360)
speed = 10.0
pos_lat  =  45.351603
pos_long = -75.918713

def sighandler(signum, frame):
    # Signal handler for exiting app
    global running
    if signum == signal.SIGINT:
        print("Received SIGINT, stopping application...")
        running = False


def method_1_callback(client, params, user_data):
    # Prints all parameters and user data.
    global download
    client.log("I'm a callback!")
    client.log(str(params))
    client.log(user_data)
    return (iot.STATUS_SUCCESS, "Return from callback")


def dump_logs(client, params, user_data):
    # Will eventually dump log files into upload directory
    return (iot.STATUS_NOT_SUPPORTED, "Not supported yet")


def file_download(client, params, user_data):
    # Downloads a file to the Device
    file_name = None
    if params:
        file_name = params.get("file_name")
    if file_name:
        client.log("Downloading")
        client.event_publish("C2D File Transfer for {}".format(file_name))
        result = client.file_download(file_name, blocking=True, timeout=15)
        if result == iot.STATUS_SUCCESS:
            message = "Downloaded!"
        else:
            message = iot.error_string(result)
        download = False
        return (result, message)
    else:
        return (iot.STATUS_BAD_PARAMETER, "No file name given")


def file_upload(client, params, user_data):
    # Uploads files to the Cloud. Supports wildcards.
    file_name = None
    if params:
        file_name = params.get("file_name")
    if file_name:
        client.log("Uploading")
        client.event_publish("D2C File Transfer for {}".format(file_name))
        result = client.file_upload(file_name, blocking=True, timeout=240)
        if result == iot.STATUS_SUCCESS:
            message = "Uploaded!"
        else:
            message = iot.error_string(result)
        download = True
        return (result, message)
    else:
        return (iot.STATUS_BAD_PARAMETER, "No file name given")


def toggle_telem( client, params, user_data ):
    # Turns Telemetry on or off
    global sending_telemetry
    sending_telemetry = not sending_telemetry
    client.log("{} sending telemetry".format(
        "Now" if sending_telemetry else "No longer"))
    return (iot.STATUS_SUCCESS, "Turned On" if sending_telemetry else "Turned Off")


def toggle_loc( client, params, user_data ):
    # Turns Location on or off
    global sending_location
    sending_location = not sending_location
    client.log("{} sending location".format(
        "Now" if sending_telemetry else "No longer"))
    return (iot.STATUS_SUCCESS, "Turned On" if sending_location else "Turned Off")


def quit_me( client, params, user_data ):
    # Quits application
    global running
    running = False
    return (iot.STATUS_SUCCESS, "Cave Johnson, we're done here")


def i_dont_do_anything(client, params, user_data):
    # Garbage function to show that registering an action can only happen once
    client.log("Except this")
    return iot.STATUS_SUCCESS


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler)
    # Initialize client called 'device_manager_demo'
    client = iot.Client("device_manager_demo")

    # Set action callbacks
    #client.action_register_callback("method_1", method_1_callback, "This is user data")
    client.action_register_command("method_1", "echo")
    client.action_register_callback("file_download", file_download)
    client.action_register_callback("file_upload", file_upload)
    client.action_register_callback("dump_logs", dump_logs)
    client.action_register_callback("toggle_telemetry", toggle_telem)
    client.action_register_callback("toggle_location", toggle_loc)
    client.action_register_callback("quit", quit_me)
    try:
        # This should fail
        client.action_register_callback("quit", i_dont_do_anything)
    except Exception as e:
        print("Exception")
        print(repr(e))

    # Telemetry names (properties for numbers, attributes for strings)
    properties = ["property-1", "property-2"]
    attributes = ["attribute-1", "attribute-2"]

    # Connect to Cloud
    if client.connect(timeout=10) != iot.STATUS_SUCCESS:
        client.error("Failed")
        sys.exit(1)

    counter = 0
    while running and client.is_connected():
        sleep(1)
        counter += 1
        if sending_telemetry and counter >= TELEMINTERVAL:
            # Randomly generate telemetry and attributes to send
            for p in properties:
                value = round(random.random()*1000, 2)
                client.log("Publishing {} to {}".format(value, p))
                client.telemetry_publish(p, value)
            for a in attributes:
                value = "".join(random.choice("abcdefghijklmnopqrstuvwxyz")
                        for x in range(20))
                client.log("Publishing {} to {}".format(value, a))
                client.attribute_publish(a, value)

            if sending_location:
                # Randomly generate location data
                speed = round(random.uniform(0, 100), 2)
                heading += round(random.random() * 20, 2) - 10
                if heading > 360:
                    heading -= 360
                if heading < 0:
                    heading += 360
                pos_lat  += round((speed * math.cos(math.radians(heading))) * 0.001, 2)
                pos_long += round((speed * math.sin(math.radians(heading))) * 0.001, 2)

                client.log("Publishing Location")
                client.location_publish(pos_lat, pos_long, heading=heading, speed=speed)

            # Reset counter after sending telemetry
            counter = 0

    client.disconnect(wait_for_replies=True)

