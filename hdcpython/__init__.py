"""
This module contains the Client class required for applications to connect and
interact with the Wind River Helix Device Cloud 2.Next.
"""

from logging import CRITICAL as LOGCRITICAL
from logging import ERROR as LOGERROR
from logging import DEBUG as LOGDEBUG
from logging import INFO as LOGINFO
from logging import NOTSET as LOGNOTSET
from logging import WARNING as LOGWARNING

from hdcpython.client import Client
from hdcpython.handler import status_string

from hdcpython.constants import DEFAULT_CONFIG_DIR
from hdcpython.constants import DEFAULT_CONFIG_FILE
from hdcpython.constants import DEFAULT_KEEP_ALIVE
from hdcpython.constants import DEFAULT_LOOP_TIME
from hdcpython.constants import DEFAULT_THREAD_COUNT

from hdcpython.constants import STATUS_SUCCESS
from hdcpython.constants import STATUS_INVOKED
from hdcpython.constants import STATUS_BAD_PARAMETER
from hdcpython.constants import STATUS_BAD_REQUEST
from hdcpython.constants import STATUS_EXECUTION_ERROR
from hdcpython.constants import STATUS_EXISTS
from hdcpython.constants import STATUS_FILE_OPEN_FAILED
from hdcpython.constants import STATUS_FULL
from hdcpython.constants import STATUS_IO_ERROR
from hdcpython.constants import STATUS_NO_MEMORY
from hdcpython.constants import STATUS_NO_PERMISSION
from hdcpython.constants import STATUS_NOT_EXECUTABLE
from hdcpython.constants import STATUS_NOT_FOUND
from hdcpython.constants import STATUS_NOT_INITIALIZED
from hdcpython.constants import STATUS_OUT_OF_RANGE
from hdcpython.constants import STATUS_PARSE_ERROR
from hdcpython.constants import STATUS_TIMED_OUT
from hdcpython.constants import STATUS_TRY_AGAIN
from hdcpython.constants import STATUS_NOT_SUPPORTED
from hdcpython.constants import STATUS_FAILURE

import hdcpython.ota_handler as ota

__all__ = ["Client",
           "status_string",
           "ota",
           "DEFAULT_CONFIG_DIR",
           "DEFAULT_CONFIG_FILE",
           "DEFAULT_KEEP_ALIVE",
           "DEFAULT_LOOP_TIME",
           "DEFAULT_RUNTIME_DIR",
           "DEFAULT_THREAD_COUNT",
           "LOGCRITICAL",
           "LOGERROR",
           "LOGDEBUG",
           "LOGINFO",
           "LOGNOTSET",
           "LOGWARNING",
           "STATUS_SUCCESS",
           "STATUS_INVOKED",
           "STATUS_BAD_PARAMETER",
           "STATUS_BAD_REQUEST",
           "STATUS_EXECUTION_ERROR",
           "STATUS_EXISTS",
           "STATUS_FILE_OPEN_FAILED",
           "STATUS_FULL",
           "STATUS_IO_ERROR",
           "STATUS_NO_MEMORY",
           "STATUS_NO_PERMISSION",
           "STATUS_NOT_EXECUTABLE",
           "STATUS_NOT_FOUND",
           "STATUS_NOT_INITIALIZED",
           "STATUS_OUT_OF_RANGE",
           "STATUS_PARSE_ERROR",
           "STATUS_TIMED_OUT",
           "STATUS_TRY_AGAIN",
           "STATUS_NOT_SUPPORTED",
           "STATUS_FAILURE"]
