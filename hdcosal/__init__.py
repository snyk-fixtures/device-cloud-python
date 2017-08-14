"""
Helix Device Cloud Operating System Abstraction Layer (OSAL).
This module provides abstractions of functions that are different depending on
operating system, allowing for cleaner, more portable code.
"""

from hdcosal.osal import system_reboot
from hdcosal.osal import system_shutdown
from hdcosal.osal import os_name
from hdcosal.osal import os_version
from hdcosal.osal import os_kernel

from hdcosal.osal import NOT_SUPPORTED

from hdcosal.osal import LINUX
from hdcosal.osal import WIN32
from hdcosal.osal import MACOS
from hdcosal.osal import POSIX
from hdcosal.osal import OTHER
