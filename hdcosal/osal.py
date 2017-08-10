"""
Operating System Abstraction Layer (OSAL). This module provides abstractions of
functions that are different on different operating systems.
"""

import os
import platform
import sys

# Constants
NOT_SUPPORTED = -20

# Setup platform info statics
WIN32 = sys.platform.startswith('win32')
LINUX = sys.platform.startswith('linux')
MACOS = sys.platform.startswith('darwin')
POSIX = LINUX or MACOS
OTHER = not POSIX and not WIN32

# Define Functions
def system_reboot(delay=0, force=True):
    """
    Reboot the system.
    """
    return system_shutdown(delay=delay, reboot=True, force=force)

def system_shutdown(delay=0, reboot=False, force=True):
    """
    Run the system shutdown command. Can be used to reboot the system.
    """
    command = "shutdown "
    if POSIX:
        command += "-r " if reboot else "-h "
        command += "now " if delay == 0 else "+{} ".format(delay)
    elif WIN32:
        command += "/r " if reboot else "/s "
        command += "/t {} ".format(delay*60)
        command += "/f" if force else ""
    else:
        return NOT_SUPPORTED

    return os.system(command)

def os_name():
    """
    Get the operating system name
    """
    name = "Unknown"
    if LINUX:
        distro = platform.linux_distribution()
        name = "{} ({})".format(distro[0], platform.system())
    elif WIN32:
        name = platform.system()
    return name

def os_version():
    """
    Get the operating system version
    """
    ver = "Unknown"
    if LINUX:
        distro = platform.linux_distribution()
        ver = "{}-{}".format(distro[1], distro[2])
    elif WIN32:
        ver = platform.release()
    return ver

def os_kernel():
    """
    Get the operating system's kernel version
    """
    ker = "Unknown"
    if LINUX:
        ker = platform.release()
    elif WIN32:
        ker = platform.version()
    return ker
