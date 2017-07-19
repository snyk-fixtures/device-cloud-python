Wind River Python Agent for HDC 2.Next
======================================

Beginning implementation for pure Python agent for the latest iteration of HDC.
It is being developed alongside the C agent so many things are subject to change
as features are ironed out on that side, and more input is received. It is
recommended to make a wrapper package for testing purposes as none of the APIs
are necessarily final.

Requirements:
- Python 2.7.9 or later
- paho-mqtt
- requests
(The last two can be obtained with `sudo pip install` and the package name)

Purpose:
The Python agent is designed for quick deployment on any platform that supports
Python.

So far supports:
- Documented user APIs (can be obtained by running `pydoc hdcpython.client`)
- Telemetry (known as properties on the Cloud side)
- Attributes (string telemetry)
- Actions (both function callbacks and console commands. Known as methods on
  Cloud side)
- File transfer (upload and download from the respective runtime directories.
  Additionally, file upload supports unix filename wildcards for uploading
  multiple files at once)
- Secure connection with TLS/SSL (this includes MQTT over TLSv1.2 and also HTTPS
  file transfer)
- Configuration files (parses the standard iot-connect.cfg and iot.cfg files for
  Cloud connection information. Currently they are found by default in the
  working directory instead of a system directory)
- Example app (example of most APIs in use, but also still a work in progress)
- Logging to console with optional logging to a specified file
- Event message publishing

Not yet supported:
- Python packaging (only comes as loose files for now)
- pytest implementation (for coverage and unit tests)
- Proxy support (may not be possible for paho)
- Finalized APIs
- Alarms
- Logging functions included in pydocs
- Return values in pydocs
