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
A script that executes an application which publishes known values to the Cloud
with the purpose of validating the abilities of the host to run the helix agent.
In the Cloud there must be a thing definition with:
  - method "pass_action" with one string parameter "param"
  - method "fail_action" with no parameters
  - property "property"
  - attribute "attribute"
  - alarm "alarm" with a possible state of 1
There must also be an associated application with "validat" in the name so the
token can be discovered.
"""

import getpass
import json
import os
import requests
import subprocess
import sys
import time

from datetime import datetime


if sys.version_info.major == 2:
    input = raw_input


app_file = "validate_app.py"
cloud = ""
validate_app = None


def _send(data, session_id=None):
    headers = None
    if session_id:
        headers = {"sessionId":session_id}
    datastr = json.dumps(data)
    r = requests.post("https://"+cloud+"/api", headers=headers, data=datastr)
    if r.status_code == 200:
        try:
            rjson = r.json()
            if "auth" in rjson:
                ret = rjson["auth"]
            elif "cmd" in rjson:
                ret = rjson["cmd"]
            return ret
        except Exception as error:
            print(error)
    return {"success":False, "content":r.content,"status_code":r.status_code}


def get_alarm(session_id, thing_key, alarm_name):
    """
    Retrieve the last value of a sent alarm
    """

    data_params = {"thingKey":thing_key,"key":alarm_name}
    data = {"cmd":{"command":"alarm.current","params":data_params}}
    return _send(data, session_id)


def get_apps(session_id):
    """
    Retreive a list of applications and their tokens
    """

    data = {"cmd":{"command":"app.list"}}
    return _send(data, session_id)


def get_attribute(session_id, thing_key, attr_name):
    """
    Retrieve the last value of a sent attribute
    """

    data_params = {"thingKey":thing_key,"key":attr_name}
    data = {"cmd":{"command":"attribute.current","params":data_params}}
    return _send(data, session_id)


def get_files(session_id, thing_key):
    """
    Retrieve a list of a specified thing's files
    """

    data_params = {"thingKey":thing_key}
    data = {"cmd":{"command":"file.list","params":data_params}}
    return _send(data, session_id)


def get_location(session_id, thing_key):
    """
    Retrieve last location of a specified thing
    """

    data_params = {"thingKey":thing_key}
    data = {"cmd":{"command":"location.current","params":data_params}}
    return _send(data, session_id)


def get_logs(session_id, thing_key, start=None):
    """
    Retrive logs from the Cloud
    """

    data_params = {"thingKey":thing_key}
    if start:
        data_params.update({"start":start})
    data = {"cmd":{"command":"log.list","params":data_params}}
    return _send(data, session_id)


def get_property(session_id, thing_key, prop_name):
    """
    Retrieve the last value of a sent property
    """

    data_params = {"thingKey":thing_key,"key":prop_name}
    data = {"cmd":{"command":"property.current","params":data_params}}
    return _send(data, session_id)


def get_session(username, password):
    """
    Get session for future communications with Cloud
    """

    data_params = {"username":username,"password":password}
    data = {"auth":{"command":"api.authenticate","params":data_params}}
    return _send(data)


def get_thing(session_id, thing_key):
    """
    Get information about a specific thing
    """

    data_params = {"key":thing_key}
    data = {"cmd":{"command":"thing.find","params":data_params}}
    return _send(data, session_id)

def delete_thing(session_id, thing_key):
    """
    delete the test thing
    """

    data_params = {"key":thing_key}
    data = {"cmd":{"command":"thing.delete","params":data_params}}
    return _send(data, session_id)

def method_exec(session_id, thing_key, method_name, params=None):
    """
    Execute Method
    """

    data_params = {"thingKey":thing_key,"method":method_name,"ackTimeout":30}
    if params:
        data_params["params"] = params
    data = {"cmd":{"command":"method.exec","params":data_params}}
    return _send(data, session_id)


def stop_app(proc):
    """
    Stop application by sending a newline to stdin
    """

    if proc:
        if proc.poll() is None:
            out = proc.communicate("\n")
            proc.wait()


def error_quit(*args):
    """
    Print error messages, stop application, and exit with error code 1
    """

    for arg in args:
        if arg.__class__.__name__ == "str":
            print(arg)
        elif arg.__class__.__name__ == "Popen":
            stop_app(arg)
    sys.exit(1)


def strtotime(string):
    """
    Convert string to a datetime object
    """

    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")


def timetostr(dtime):
    """
    Convert datetime into a string
    """

    return dtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def main():
    """
    Main function to validate abilites of host
    """

    global cloud
    start_time = datetime.utcnow()
    fails = []
    default_device_id = "c13ae2c8-2eb3-4449-81e5-ffd8bedb63a9"

    if not os.path.isfile(app_file):
        error_quit("Could not find app file {}.".format(app_file))

    cloud = os.environ.get("HDCADDRESS")
    username = os.environ.get("HDCUSERNAME")
    password = os.environ.get("HDCPASSWORD")

    # Get Cloud credentials
    if not cloud:
        cloud = input("Cloud Address: ")
    if not username:
        username = input("Username: ")
    if not password:
        password = getpass.getpass("Password: ")

    # Ensure Cloud address is formatted correctly for later use
    cloud = cloud.split("://")[-1]
    cloud = cloud.split("/")[0]
    print("Cloud: {}".format(cloud))

    # Start a session with the Cloud
    session_id = ""
    session_info = get_session(username, password)
    if session_info.get("success") is True:
        session_id = session_info["params"].get("sessionId")
    if session_id:
        print("Session ID: {} - OK".format(session_id))
    else:
        error_quit("Failed to get session id.")

    # Look for the app token created for this validation test.
    # This token is looked for by name, so as long as the cloud has a validation
    # app set up, the token does not need to be retrieved manually.
    validateapps = []
    app_info = get_apps(session_id)
    if app_info.get("success") is True:
        app_list = app_info.get("params")
        if app_list.get("result") is not None:
            validateapps = [x for x in app_list["result"]
                            if "validat" in x["name"]]
    if len(validateapps) == 1:
        token = validateapps[0]["token"]
        print("Token: {} - OK".format(token))
    elif len(validateapps) == 0:
        error_quit("Failed to get token. An application for validation "
                   "may not exist.")
    else:
        error_quit("More than one validation application. "
                   "Not sure which one to use.")

    # Generate config for app with retrieved token
    generate = subprocess.Popen("./generate_config.py -f validate.cfg "
                                "-c "+cloud+" -p 8883 "
                                "-t "+token, shell=True,
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    ret = generate.wait()
    if ret != 0:
        error_quit("Failed to generate connection config for validation app.")

    # Remove the downloaded file if it exists from a previous validation
    if os.path.isfile(os.path.abspath("validate_download")):
        os.remove(os.path.abspath("validate_download"))

    # delete the thing in the cloud so that we don't have 100s of new
    # instances of test apps.  Write the device_id here and then check
    # the cloud.  Subsequent code will use the device_id.  This test
    # would normally be run in a docker instance with a new device_id each time.
    if os.path.isfile("device_id"):
        print("file device_id exists, using it")
    else:
        with open("device_id", "w") as did_file:
            did_file.write( default_device_id )

    thing_key = default_device_id + "-iot-validate-app"
    print("Deleting thing key {} for this test".format(thing_key))
    thing_info = delete_thing(session_id, thing_key)
    print(json.dumps(thing_info, indent=2, sort_keys=True))

    # Start app
    validate_app = subprocess.Popen("."+os.sep+app_file,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    time.sleep(2)

    # Check that the device_id has been created (or at least previously existed)
    device_id = ""
    thing_key = ""
    if os.path.isfile("device_id"):
        with open("device_id", "r") as did_file:
            device_id = did_file.read().strip()
        thing_key = device_id + "-iot-validate-app"
    if device_id:
        print("Thing Key: {} - OK".format(thing_key))
    else:
        error_quit("Device ID not found - FAIL", validate_app)

    time.sleep(1)

    # Check to make sure thing is connected in Cloud
    thing = None
    thing_info = get_thing(session_id, thing_key)
    #print(json.dumps(thing_info, indent=2, sort_keys=True))
    if thing_info.get("success") is True:
        thing = thing_info.get("params")
    if thing:
        connected = thing.get("connected")
        if connected is True:
            print("Connected - OK")
        else:
            error_quit("Thing not connected - FAIL", validate_app)
    else:
        error_quit("Thing not found in Cloud - FAIL", validate_app)

    # Check that the expected property value was published to the Cloud
    prop = None
    prop_info = get_property(session_id, thing_key, "property")
    #print(json.dumps(prop_info, indent=2, sort_keys=True))
    if prop_info.get("success") is True:
        prop = prop_info.get("params")
    if prop:
        if (strtotime(prop["ts"]) > start_time and
                strtotime(prop["ts"]) < datetime.utcnow()):
            if prop["value"] == 12.34:
                print("Property: {} - OK".format(prop["value"]))
            else:
                print("Wrong property value: {} != 12.34 "
                      "- FAIL".format(prop["value"]))
                fails.append("Property value")
        else:
            print("Property timestamp out of range of application - FAIL")
            fails.append("Property time")
    else:
        print("Property not found in Cloud - FAIL")
        fails.append("Property retrieval")

    # Check that the expected atribute value was published to the Cloud
    attr = None
    attr_info = get_attribute(session_id, thing_key, "attribute")
    #print(json.dumps(attr_info, indent=2, sort_keys=True))
    if attr_info.get("success") is True:
        attr = attr_info.get("params")
    if attr:
        if (strtotime(attr["ts"]) > start_time and
                strtotime(attr["ts"]) < datetime.utcnow()):
            if attr["value"] == "text and such":
                print("Attribute: \"{}\" - OK".format(attr["value"]))
            else:
                print("Wrong attribute value: {} != \"text and such\" - FAIL".format(attr["value"]))
                fails.append("Attribute value")
        else:
            print("Attribute timestamp out of range of application - FAIL")
            fails.append("Attribute time")
    else:
        print("Attribute not found in Cloud - FAIL")
        fails.append("Attribute retrieval")

    # Check that the expected location was published to the Cloud
    loc = None
    loc_info = get_location(session_id, thing_key)
    #print(json.dumps(loc_info, indent=2, sort_keys=True))
    if loc_info.get("success") is True:
        loc = loc_info.get("params")
    if loc:
        errors = []
        if loc["lat"] != 45.351603:
            errors.append("lat: {} != 45.351603".format(loc["lat"]))
        if loc["lng"] != -75.918713:
            errors.append("lng: {} != ".format(loc["lng"]))
        if loc["heading"] != 12.34:
            errors.append("heading: {} != 12.34".format(loc["heading"]))
        if loc["altitude"] != 1.0:
            errors.append("altitude: {} != 1.0".format(loc["altitude"]))
        if loc["speed"] != 2.0:
            errors.append("speed: {} != 2.0".format(loc["speed"]))
        if loc["fixAcc"] != 3.0:
            errors.append("fixAcc: {} != 3.0".format(loc["fixAcc"]))
        if loc["fixType"] != "crystal ball":
            errors.append("fix_type: {} != \"crystal ball\"".format(loc["fixType"]))
        if errors:
            print("Wrong location: {} - FAIL".format(", ".join(errors)))
            fails.append("Location")
        else:
            print("Location: lat:{}, lng:{}, etc... - OK".format(loc["lat"], loc["lng"]))
    else:
        print("Location not found in Cloud - FAIL")
        fails.append("Location retrieval")

    # Check that the expected log was published to the Cloud
    logs = None
    logs_info = get_logs(session_id, thing_key, start=timetostr(start_time))
    #print(json.dumps(logs_info, indent=2, sort_keys=True))
    if logs_info.get("success") is True:
        logs = logs_info.get("params")
    if logs and logs.get("result") is not None:
        correct = filter(lambda x: x["msg"] == "logs and such" and
                                   x["thingKey"] == thing_key,
                         logs["result"])
        if len(correct) == 1:
            print("Log: \"{}\" - OK".format(correct[0]["msg"]))
        elif len(correct) == 0:
            print("No logs for this thing in the specified time frame - FAIL")
            fails.append("Log retrieval")
        else:
            print("Multiple logs found. Double sending? - FAIL")
            fails.append("Possible log double-sending")
    else:
        print("Logs could not be retrieved - FAIL")
        fails.append("Log retrieval")

    # Check that the pass action executes and returns successfully
    pass_act_info = method_exec(session_id, thing_key, "pass_action",
                                {"param":"value"})
    #print(json.dumps(pass_act_info, indent=2, sort_keys=True))
    if pass_act_info.get("success") is True:
        print("Pass action success: True - OK")
    else:
        print("Pass action failed to complete successfully - FAIL")
        fails.append("Action successful execution")

    # Check that the fail action executes and returns a failure successfully
    fail_act_info = method_exec(session_id, thing_key, "fail_action")
    #print(json.dumps(fail_act_info, indent=2, sort_keys=True))
    if fail_act_info.get("success") is False:
        errmsgs = fail_act_info.get("errorMessages")
        if len(errmsgs) == 1 and errmsgs[0] == "fail and such":
            print("Fail action error message: \"fail and such\" - OK")
        else:
            print("Fail action error message: \"{}\" != \"fail and such\" - "
                  "FAIL".format(errmsgs[0]))
            fails.append("Action error message")
    else:
        print("Fail action did not return failure - FAIL")
        fails.append("Action failure")

    # Check that a file was successfully uploaded to the Cloud
    tries = 50
    while tries > 0:
        tries -= 1
        time.sleep(0.5)
        files = None
        files_info = get_files(session_id, thing_key)
        #print(json.dumps(files_info, indent=2, sort_keys=True))
        if files_info.get("success") is True:
            files = files_info.get("params")
        if files and files.get("result") is not None:
            correct = filter(lambda x: x["fileName"] == "validate_upload" and
                                       strtotime(x["uploadDate"]) > start_time,
                             files["result"])
            if len(correct) == 1:
                print("File uploaded: validate_upload - OK")
                break
            elif len(correct) == 0:
                if tries == 0:
                    print("No files found in Cloud with specified name and "
                          "time frame - FAIL")
                    fails.append("File not in file list")
            else:
                if tries == 0:
                    print("Multiple files with the same name...? - FAIL")
                    fails.append("File list contains duplicates")
        else:
            if tries == 0:
                print("File list could not be retrieved - FAIL")
                fails.append("File list retrieval")

    # Check that a file was successfully downloaded from the Cloud
    tries = 20
    while tries > 0:
        tries -= 1
        time.sleep(0.5)
        if os.path.isfile(os.path.abspath("validate_download")):
            print("File downloaded: validate_download - OK")
            break
        else:
            if tries == 0:
                print("Could not found downloaded file - FAIL")
                fails.append("Download file")

    stop_app(validate_app)
    return fails


if __name__ == "__main__":
    fails = []
    try:
        fails = main()
    except Exception as error:
        stop_app(validate_app)
        raise(error)
    if not fails:
        print("\n\nAll passed! Success.")
        sys.exit(0)
    else:
        print("\n\nFailed on the following:")
        for fail in fails:
            print(fail)
        sys.exit(1)


