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
This module contains all the constant values required by the Client
"""

# CONFIGURATION DEFAULTS

# Default configuration directory
DEFAULT_CONFIG_DIR = "."
# Default configuration file name
# {} is replaced with app id
DEFAULT_CONFIG_FILE = "{}-connect.cfg"
# Number of seconds to attempt to reconnect if disconnected
# 0 means retry forever
DEFAULT_KEEP_ALIVE = 0
# Default loop time for MQTT in seconds
DEFAULT_LOOP_TIME = 1
# Default number of worker threads
DEFAULT_THREAD_COUNT = 3


# PORTS THAT REQUIRE SSL CONNECTIONS

SECURE_PORTS = [
    443,
    8883
]


# CONNECTION STATES

# Not connected to Cloud
STATE_DISCONNECTED = 0
# Connecting to Cloud
STATE_CONNECTING = 1
# Connected to Cloud
STATE_CONNECTED = 2


# RETURN STATUSES

# Success
STATUS_SUCCESS = 0
# Action successfully invoked (fire & forget)
STATUS_INVOKED = 1
# Invalid parameter passed
STATUS_BAD_PARAMETER = 2
# Bad request received
STATUS_BAD_REQUEST = 3
# Error executing the requested action
STATUS_EXECUTION_ERROR = 4
# Already exists
STATUS_EXISTS = 5
# File open failed
STATUS_FILE_OPEN_FAILED = 6
# Full storage
STATUS_FULL = 7
# Input/output error
STATUS_IO_ERROR = 8
# No memory
STATUS_NO_MEMORY = 9
# No permission
STATUS_NO_PERMISSION = 10
# Not executable
STATUS_NOT_EXECUTABLE = 11
# Not found
STATUS_NOT_FOUND = 12
# Not Initialized
STATUS_NOT_INITIALIZED = 13
# Parameter out of range
STATUS_OUT_OF_RANGE = 14
# Failed to parse a message
STATUS_PARSE_ERROR = 15
# Timed out
STATUS_TIMED_OUT = 16
# Try again
STATUS_TRY_AGAIN = 17
# Not supported in this version of the api
STATUS_NOT_SUPPORTED = 18
# General Failure
STATUS_FAILURE = 19


# STATUS STRINGS
STATUS_STRINGS = {
    STATUS_SUCCESS:"Success",
    STATUS_INVOKED:"Invoked",
    STATUS_BAD_PARAMETER:"Bad Parameter",
    STATUS_BAD_REQUEST:"Bad Request",
    STATUS_EXECUTION_ERROR:"Execution Error",
    STATUS_EXISTS:"Already Exists",
    STATUS_FILE_OPEN_FAILED:"File Open Failed",
    STATUS_FULL:"Full",
    STATUS_IO_ERROR:"I/O Error",
    STATUS_NO_MEMORY:"Out of Memory",
    STATUS_NO_PERMISSION:"No Permission",
    STATUS_NOT_EXECUTABLE:"Not Executable",
    STATUS_NOT_FOUND:"Not Found",
    STATUS_NOT_INITIALIZED:"Not Initialized",
    STATUS_OUT_OF_RANGE:"Out of Range",
    STATUS_PARSE_ERROR:"Parsing Error",
    STATUS_TIMED_OUT:"Timed Out",
    STATUS_TRY_AGAIN:"Try Again",
    STATUS_NOT_SUPPORTED:"Not Supported",
    STATUS_FAILURE:"Failure"
}


# Log message format
LOG_FORMAT = "%(asctime)s %(levelname)s: %(filename)s:%(lineno)d - %(message)s"
# Log time format
LOG_TIME_FORMAT = "%b %d %H:%M:%S"

# Time format supported by Cloud
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


# TYPES OF WORK

# Parse a received message
WORK_MESSAGE = 0
# Publish pending publishes
WORK_PUBLISH = 1
# Execute a requested action
WORK_ACTION = 2
# Download a file
WORK_DOWNLOAD = 3
# Upload a file
WORK_UPLOAD = 4
