
import constants
import Queue
import subprocess
import threading

from datetime import datetime

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
        return "Action {} --> Callback {}".format(self.name,
                self.callback.__name__)

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
        final_command = self.command
        if params:
            for key in params:
                if params[key] == True:
                    # Value is True, just append flag
                    final_command += " --{}".format(key)
                elif params[key] == False:
                    # Value is False, do not append flag
                    pass
                else:
                    # Append --param=value
                    final_command += " --{}={}".format(key, params[key])

        # Execute command with arguments and wait for result
        proc = subprocess.Popen(final_command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outstr, errstr = proc.communicate()
        proc.wait()
        ret_code = proc.returncode

        return (ret_code, "command: {}  ,  stdout: {}  ,  stderr: {}".format(
                final_command, outstr, errstr))


class ActionRequest(object):
    """
    Holds information about action requests for execution
    """

    def __init__(self, id, name, params):
        self.id = id
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
        if not self.__contains__(action_request.name):
            raise KeyError("Action \"{}\" does not have a callback".format(
                    action_request.name))
        else:
            result = self.__getitem__(action_request.name).execute(
                    action_request.params)

        return result

    def remove_action(self, action_name):
        """
        Remove an action callback as long as it exists
        """

        if not self.__contains__(action.name):
            raise KeyError("Action \"{}\" does not have a callback".format(
                    action.name))
        else:
            self.__delitem__(action.name)


class Config(dict):
    """
    Holds all configuration information about the Client
    """

    def __init__(self, cfg):
        """
        Parse a dict to determine aspects of the configuration
        """

        super(Config, self).__init__()

        # Add every config item, only one level deep
        for key in cfg:
            if cfg[key].__class__.__name__ == "dict":
                for subkey in cfg[key]:
                    if cfg[key][subkey]:
                        self["{}_{}".format(key, subkey)] = cfg[key][subkey]
            else:
                if cfg[key]:
                    self[key] = cfg[key]


        # Handle defaults
        self.setdefault("log_level", constants.DEFAULT_LOG_LEVEL)
        self.setdefault("loop_time", constants.DEFAULT_LOOP_TIME)
        self.setdefault("message_timeout", constants.DEFAULT_MESSAGE_TIMEOUT)
        self.setdefault("runtime_dir", constants.DEFAULT_RUNTIME_DIR)
        self.setdefault("thread_count", constants.DEFAULT_THREAD_COUNT)

        # Handle key
        if self.get("name") and self.get("device_id"):
            self["key"] = "{}-{}".format(self.device_id, self.name)

        # Handle validate_cert boolean
        if self.get("validate_cloud_cert"):
            self["validate_cloud_cert"] = (self["validate_cloud_cert"].lower()
                    == "true")

    def __getattribute__(self, attr):
        try:
            return super(Config, self).__getattribute__(attr)
        except:
            return self.get(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


class FileTransfer(object):
    """
    Holds information about pending file transfers
    """

    def __init__(self, fileName, fileId=None, fileChecksum=None):
        self.fileName = fileName
        self.fileId = fileId
        self.fileChecksum = fileChecksum
        self.status = None


class Location(object):
    """
    Holds location information
    """

    def __init__(self, latitude, longitude, heading=None, altitude=None,
            speed=None, accuracy=None, fix_type=None):
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

    def __init__(self, command, description, ts=None, data=None, id=None):
        self.command = command
        self.description = description
        self.ts = ts
        self.data = data
        self.id = id

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

        self[message.id] = message

    def pop_message(self, topic_num, cmd_num):
        """
        Remove a single message
        """

        id = "{}-{}".format(topic_num, cmd_num)
        try:
            message = self.pop(id)
        except KeyError:
            raise KeyError("Message {} not found. May have already timed "
                    "out".format(id))
        return message

    def time_out(self, current_time, max_time):
        """
        Remove and return a list of all messages that have timed out
        """

        to_remove = []
        for id in self:
            message = self[id]
            if ((current_time - message.ts).total_seconds() > max_time):
                to_remove.append(id)

        removed = []
        for id in to_remove:
            removed.append(self.pop_message(*(id.split("-"))))

        return removed


class Telemetry(object):
    """
    Holds information about telemetry (and other data) that is to be published
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.ts = datetime.utcnow().strftime(constants._TIME_FORMAT)
        self.type = value.__class__.__name__


class Log(Telemetry):
    """
    Holds a log message to be sent to the Cloud
    """

    def __init__(self, message):
        super(Log, self).__init__("log", message)
        self.type = "Log"


class Work(object):
    """
    Holds information about work that needs to be completed
    """

    def __init__(self, work_type, data):
        self.type = work_type
        self.data = data


