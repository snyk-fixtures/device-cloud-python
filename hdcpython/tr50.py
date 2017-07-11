
import defs
import json

from constants import *

_cloud_error_codes = {
        STATUS_SUCCESS:0,
        STATUS_INVOKED:STATUS_INVOKED,
        STATUS_BAD_PARAMETER:STATUS_BAD_PARAMETER,
        STATUS_BAD_REQUEST:STATUS_BAD_REQUEST,
        STATUS_EXECUTION_ERROR:STATUS_EXECUTION_ERROR,
        STATUS_EXISTS:STATUS_EXISTS,
        STATUS_FILE_OPEN_FAILED:STATUS_FILE_OPEN_FAILED,
        STATUS_FULL:STATUS_FULL,
        STATUS_IO_ERROR:STATUS_IO_ERROR,
        STATUS_NO_MEMORY:STATUS_NO_MEMORY,
        STATUS_NO_PERMISSION:STATUS_NO_PERMISSION,
        STATUS_NOT_EXECUTABLE:STATUS_NOT_EXECUTABLE,
        STATUS_NOT_FOUND:STATUS_NOT_FOUND,
        STATUS_NOT_INITIALIZED:STATUS_NOT_INITIALIZED,
        STATUS_OUT_OF_RANGE:STATUS_OUT_OF_RANGE,
        STATUS_PARSE_ERROR:STATUS_PARSE_ERROR,
        STATUS_TIMED_OUT:STATUS_TIMED_OUT,
        STATUS_TRY_AGAIN:STATUS_TRY_AGAIN,
        STATUS_NOT_SUPPORTED:STATUS_NOT_SUPPORTED,
        STATUS_FAILURE:STATUS_FAILURE}


class TR50Command:
    """
    Holds all relevant TR50 command names
    """

    alarm_publish = "alarm.publish"
    attribute_current = "attribute.current"
    attribute_publish = "attribute.publish"
    diag_echo = "diag.echo"
    diag_ping = "diag.ping"
    file_get = "file.get"
    file_put = "file.put"
    location_publish = "location.publish"
    log_publish = "log.publish"
    mailbox_ack = "mailbox.ack"
    mailbox_check = "mailbox.check"
    mailbox_update = "mailbox.update"
    property_publish = "property.publish"
    thing_find = "thing.find"


def _generate_params(kwargs):
    """
    Generate JSON based on the arguments passed to this function
    """

    params = {}
    for key in kwargs:
        if kwargs[key] != None:
            params[key] = kwargs[key]
    return params

def create_alarm_publish(thingKey, key, state, msg=None, ts=None, corrId=None,
        lat=None, lng=None, republish=None):
    """
    Generate a TR50 JSON request for publishing an alarm
    """

    kwargs = locals()
    cmd = {"command":TR50Command.alarm_publish}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_attribute_current(thingKey, key, ts=None):
    """
    Generate a TR50 JSON request for getting an attribute's current value
    """

    kwargs = locals()
    cmd = {"command":TR50Command.attribute_current}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_attribute_publish(thingKey, key, value, ts=None, republish=None ):
    """
    Generate a TR50 JSON request for publishing a string value
    """

    kwargs = locals()
    cmd = {"command":TR50Command.attribute_publish}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_diag_echo(thingKey, params):
    """
    Generate a TR50 JSON request for a diagnostic echo
    """

    kwargs = locals()
    cmd = {"command":TR50Command.diag_echo}
    cmd["params"] = params
    return cmd

def create_diag_ping():
    """
    Generate a TR50 JSON request for a diagnostic ping
    """

    cmd = {"command":TR50Command.diag_ping}
    return cmd

def create_file_get(thingKey, fileName):
    """
    Generate a TR50 JSON request for getting a file from the Cloud
    """

    kwargs = locals()
    cmd = {"command":TR50Command.file_get}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_file_put(thingKey, fileName, public=False, crc32=None, tags=None,
        secTags=None, ttl=None, logComplete=None):
    """
    Generate a TR50 JSON request for putting a file in the Cloud
    """

    kwargs = locals()
    cmd = {"command":TR50Command.file_put}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_location_publish(thingKey, lat, lng, heading=None, altitude=None,
        speed=None,  fixAcc=None, fixType=None, ts=None, corrId=None,
        debounce=None, streetNumber=None, street=None, city=None, state=None,
        zipCode=None, country=None ):
    """
    Generate a TR50 JSON request for publishing a location to the Cloud
    """

    kwargs = locals()
    cmd = {"command":TR50Command.location_publish}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_log_publish(thingKey, msg, ts=None, level=None, corrId=None,
        globalLog=None):
    """
    Generate a TR50 JSON request for publishing a log entry to the Cloud
    """

    kwargs = locals()
    # Handle globalLog because global is a keyword
    kwargs["global"] = globalLog
    del kwargs["globalLog"]
    cmd = {"command":TR50Command.log_publish}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_mailbox_ack(id, errorCode=None, errorMessage=None, params=None):
    """
    Generate a TR50 JSON request for acknowledging the execution of an action
    """

    kwargs = locals()
    cmd = {"command":TR50Command.mailbox_ack}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_mailbox_check(autoComplete, limit=None):
    """
    Generate a TR50 JSON request for checking the mailbox in the Cloud
    """

    kwargs = locals()
    cmd = {"command":TR50Command.mailbox_check}
    params = _generate_params(kwargs)
    if params:
        cmd["params"] = params
    return cmd

def create_mailbox_update(id, msg):
    """
    Generate a TR50 JSON request for updating a mailbox message
    """

    kwargs = locals()
    cmd = {"command":TR50Command.mailbox_update}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_property_publish(thingKey, key, value, ts=None, corrId=None,
        aggregate=None):
    """
    Generate a TR50 JSON request for publishing a numeric value to the Cloud
    """

    kwargs = locals()
    cmd = {"command":TR50Command.property_publish}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def create_thing_find(key):
    """
    Generate a TR50 JSON request for finding a different registered app
    """

    kwargs = locals()
    cmd = {"command":TR50Command.thing_find}
    cmd["params"] = _generate_params(kwargs)
    return cmd

def generate_request(commands):
    """
    Generate a final TR50 request string out of multiple commands
    """

    request = {}

    # Ensure we are working with a list
    command_list = commands
    if commands.__class__.__name__ != "list":
        command_list = [commands]

    # Add each command to the request
    for i in range(len(command_list)):
        request[str(i+1)] = command_list[i]

    return json.dumps(request)

def translate_error_code(error_code):
    """
    Return the related Cloud error code for a given device error code
    """

    return (_cloud_error_codes.get(error_code) if error_code in
            _cloud_error_codes else error_code)
