Wind River Python Agent for HDC 2.Next
======================================

Beginning implementation for pure Python agent for the latest iteration of HDC.
It is being developed alongside the C agent so many things are subject to change
as features are ironed out on that side, and more input is received. It is
recommended to make a wrapper package for testing purposes as none of the APIs
are necessarily final.


Purpose:
The Python agent is designed for quick deployment on any platform that supports
Python.


Requirements:
- Python 2.7.9 or later
- paho-mqtt
- requests

(The last two can be obtained with `sudo pip install` and the package name, or 
by running `pip install .`, which will install the module and its dependencies)

Pip Installation:

The module can be installed locally for ease of use by running `pip install .`
in the root directory of the cloned repository. This will install the module and
its dependencies. The agent can then be imported into other Python scripts as
normal (`import hdcpython`).

So far supports:
- Documented user APIs (can be obtained by running `pydoc hdcpython`)
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
- Alarm publishing
- pytest implementation start. Run `pytest -v .` to run unit tests.
  `pytest --cov-report=html --cov=hdcpython -v .` Will generate a directory
  containing an HTML report of coverage.


Not yet supported:
- Python packaging (only comes as loose files for now)
- Proxy support (may not be possible for paho)
- Finalized APIs
- Logging functions included in pydocs
