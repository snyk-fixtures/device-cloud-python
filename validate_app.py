#!/usr/bin/env python

'''
    Copyright (c) 2016-2017 Wind River Systems, Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software  distributed
    under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
    OR CONDITIONS OF ANY KIND, either express or implied.
'''

"""
Simple app that validates the capabilities of the host machine to run an IOT
application.
"""

import errno
import helix
import os
import signal
import sys
from time import sleep
import coverage

log_file = open("stdout.log", "w")

def dump(msg):
    global log_file
    log_file.write(msg + "\n")

if "VALIDATE_COVERAGE" in os.environ:
    enable_cov = True
else:
    enable_cov = False

if sys.version_info.major == 2:
    input = raw_input

running = True


def sighandler(signum, frame):
    """
    Signal handler for exiting app
    """
    global running
    if signum == signal.SIGINT:
        print("Received SIGINT, stopping application...")
        running = False


def pass_action(client, params, user_data):
    if params and params["param"] == "value":
        return 0
    else:
        return 18

def fail_action(client, params, user_data):
    return (19, "fail and such")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler)

    if enable_cov == True:
        cov = coverage.Coverage()
        cov.start()

    dump("starting")
    client = helix.Client("iot-validate-app")
    client.config.config_file = "validate.cfg"

    client.initialize()

    client.action_register_callback("pass_action", pass_action)
    client.action_register_callback("fail_action", fail_action)

    if client.connect(timeout=10) != helix.STATUS_SUCCESS:
        print("Failed to connect")
        dump("Failed to connect")
        sys.exit(1)
    else:
        dump("connected ok")

    dump("publishing telemetry")
    client.telemetry_publish("property", 12.34)
    dump("publishing attributes")
    client.attribute_publish("attribute", "text and such")
    dump("publishing location")
    client.location_publish(45.351603, -75.918713, heading=12.34, altitude=1.0,
                            speed=2.0, accuracy=3.0, fix_type="crystal ball")
    dump("triggering event")
    client.event_publish("logs and such")
    dump("triggering alarm")
    client.alarm_publish("alarm", 1, "very serious alarm")

    dump("triggering file upload")
    client.file_upload(os.path.abspath(__file__), upload_name="validate_upload",
                       blocking=True, timeout=30)

    dump("triggering file download")
    client.file_download("validate_upload",
                         os.path.abspath("validate_download"),
                         blocking=True, timeout=30)

    dump("done")
    input("Hit enter to exit:")

    client.disconnect()

    if enable_cov == True:
        cov.stop()
        cov.save()
        cov.html_report(omit="/usr/local/lib/*")

    sys.exit(0)
