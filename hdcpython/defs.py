"""
This module defines several helper classes for use in the hdcpython handler
"""

import subprocess
from datetime import datetime

from hdcpython import constants

class Action(object):
    """
    Holds information associating an action and a callback
    """

    def __init__(self, name, callback, client, user_data=None):
        self.name = name
        self.callback = callback
        self.client = client
        self.user_data = user_data

    def __str__(self):
        string = "Action {} --> Callback {}"
        return string.format(self.name, self.callback.__name__)

    def execute(self, params):
        """
        Execute callback
        """

        return self.callback(self.client, params, self.user_data)


class ActionCommand(Action):
    """
    Holds information associating an action and a console command
    """

    def __init__(self, name, callback, client, user_data=None):
        super(ActionCommand, self).__init__(name, None, client, user_data)
        self.command = callback

    def __str__(self):
        return "Action {} --> Command \"{}\"".format(self.name, self.command)

    def execute(self, params):
        """
        Execute command
        """

        # Append parameters as command line arguments
        final_command = [self.command]
        if params:
            for key in params:
                if params[key] is True:
                    # Value is True, just append flag
                    final_command.append("--{}".format(key))
                elif params[key] is False:
                    # Value is False, do not append flag
                    pass
                else:
                    # Append --param=value
                    final_command.append("--{}={}".format(key, params[key]))

        # Execute command with arguments and wait for result
        proc = subprocess.Popen(final_command, shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        outstr, errstr = proc.communicate()
        ret_code = proc.returncode

        return_string = "command: {}  ,  stdout: {}  ,  stderr: {}"
        return (ret_code, return_string.format(final_command, outstr, errstr))


class ActionRequest(object):
    """
    Holds information about action requests for execution
    """

    def __init__(self, request_id, name, params):
        self.request_id = request_id
        self.name = name
        self.params = params


class Callbacks(dict):
    """
    Dict to hold all action callbacks and execute them when required
    """

    def __init__(self):
        super(Callbacks, self).__init__()

    def add_action(self, action):
        """
        Add a new action callback if an action of that name is not already
        registered
        """

        if self.__contains__(action.name):
            raise KeyError("Action \"{}\" already has a callback".format(
                action.name))
        else:
            self.__setitem__(action.name, action)

    def execute_action(self, action_request):
        """
        Execute a specific action callback from an action request
        """

        result = None

        # Attempt to execute action callback if an action with the same name as
        # the request is registered
        if action_request.name not in self:
            raise KeyError("Action \"{}\" does not have a callback".format(
                action_request.name))
        else:
            result = self[action_request.name].execute(action_request.params)

        return result

    def remove_action(self, action_name):
        """
        Remove an action callback as long as it exists
        """

        if action_name not in self:
            raise KeyError("Action \"{}\" does not have a callback".format(
                action_name))
        else:
            del self[action_name]


class Config(dict):
    """
    Holds all configuration information about the Client
    """

    def __init__(self):
        # Call dict init function
        super(Config, self).__init__()

        # Handle defaults
        self.setdefault("config_dir", constants.DEFAULT_CONFIG_DIR)
        self.setdefault("log_level", constants.DEFAULT_LOG_LEVEL)
        self.setdefault("loop_time", constants.DEFAULT_LOOP_TIME)
        self.setdefault("message_timeout", constants.DEFAULT_MESSAGE_TIMEOUT)
        self.setdefault("runtime_dir", constants.DEFAULT_RUNTIME_DIR)
        self.setdefault("thread_count", constants.DEFAULT_THREAD_COUNT)

    def __getattribute__(self, attr):
        try:
            return super(Config, self).__getattribute__(attr)
        except AttributeError:
            return self.get(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

    def update(self, other):
        # Add every dict item, only one level deep
        for key in other:
            if other[key].__class__.__name__ == "dict":
                for subkey in other[key]:
                    if other[key][subkey]:
                        self["{}_{}".format(key, subkey)] = other[key][subkey]
            else:
                if other[key]:
                    self[key] = other[key]

        # Handle key
        if self.get("name") and self.get("device_id"):
            self["key"] = "{}-{}".format(self.device_id, self.name)

        # Handle validate_cert boolean
        cloud_cert = self.get("validate_cloud_cert")
        if cloud_cert:
            self["validiate_cloud_cert"] = str(cloud_cert).lower() == "true"


class FileTransfer(object):
    """
    Holds information about pending file transfers
    """

    def __init__(self, file_name, file_id=None, file_checksum=None):
        self.file_name = file_name
        self.file_id = file_id
        self.file_checksum = file_checksum
        self.status = None


class Message(object):
    """
    Holds received messages in their json format
    """

    def __init__(self, topic, json_msg):
        self.topic = topic
        self.json = json_msg


class OutMessage(object):
    """
    Hold sent messages and their timestamps so that their replies can be handled
    """

    def __init__(self, command, description, timestamp=None, data=None,
                 out_id=None):
        self.command = command
        self.description = description
        self.timestamp = timestamp
        self.data = data
        self.out_id = out_id

    def __str__(self):
        return self.description


class OutTracker(dict):
    """
    Holds all sent messages that are waiting for a reply
    """

    def __init__(self):
        super(OutTracker, self).__init__()

    def add_message(self, message):
        """
        Add a message
        """

        self[message.out_id] = message

    def pop_message(self, topic_num, cmd_num):
        """
        Remove a single message
        """

        out_id = "{}-{}".format(topic_num, cmd_num)
        try:
            message = self.pop(out_id)
        except KeyError:
            raise KeyError("Message {} not found. May have already timed "
                           "out".format(out_id))
        return message

    def time_out(self, current_time, max_time):
        """
        Remove and return a list of all messages that have timed out
        """

        to_remove = []
        for out_id in self:
            message = self[out_id]
            if (current_time - message.timestamp).total_seconds() > max_time:
                to_remove.append(out_id)

        removed = []
        for out_id in to_remove:
            removed.append(self.pop_message(*(out_id.split("-"))))

        return removed


class Publish(object):
    """
    Super Class for holding information about a pending publish
    """

    def __init__(self):
        self.timestamp = datetime.utcnow().strftime(constants.TIME_FORMAT)
        self.type = self.__class__.__name__


class PublishAlarm(Publish):
    """
    Holds information about an alarm
    """

    def __init__(self, name, state, message=None):
        super(PublishAlarm, self).__init__()
        self.name = name
        self.state = state
        self.message = message


class PublishAttribute(Publish):
    """
    Holds information about an attribute that is to be published
    """

    def __init__(self, name, value):
        super(PublishAttribute, self).__init__()
        self.name = name
        self.value = value


class PublishLocation(Publish):
    """
    Holds location information
    """

    def __init__(self, latitude, longitude, heading=None, altitude=None,
                 speed=None, accuracy=None, fix_type=None):
        super(PublishLocation, self).__init__()
        self.latitude = latitude
        self.longitude = longitude
        self.heading = heading
        self.altitude = altitude
        self.speed = speed
        self.accuracy = accuracy
        self.fix_type = fix_type

    def __str__(self):
        string = "latitude: {}, longitude: {}".format(self.latitude,
                                                      self.longitude)
        if self.heading:
            string += ", heading: {}".format(self.heading)
        if self.altitude:
            string += ", altitude: {}".format(self.altitude)
        if self.speed:
            string += ", speed: {}".format(self.speed)
        if self.accuracy:
            string += ", accuracy: {}".format(self.accuracy)
        if self.fix_type:
            string += ", fix type: {}".format(self.fix_type)
        return string


class PublishLog(Publish):
    """
    Holds a log message to be sent to the Cloud
    """

    def __init__(self, message):
        super(PublishLog, self).__init__()
        self.message = message


class PublishTelemetry(Publish):
    """
    Holds information about telemetry that is to be published
    """

    def __init__(self, name, value):
        super(PublishTelemetry, self).__init__()
        self.name = name
        self.value = value


class Work(object):
    """
    Holds information about work that needs to be completed
    """

    def __init__(self, work_type, data):
        self.type = work_type
        self.data = data


