Wind River Python Agent for HDC 2.Next
======================================

Beginning implementation for pure Python agent for the latest iteration of HDC.
It is being developed alongside the C agent so many things are subject to change
as features are ironed out on that side, and more input is received. It is
recommended to make a wrapper package for testing purposes as none of the APIs
are necessarily final.

Purpose:
--------
The Python agent is designed for quick deployment on any platform that supports
Python.

Requirements:
-------------
- Python 2.7.9 or later
- paho-mqtt
- requests

(The last two can be obtained with `sudo pip install` and the package name, or 
by running `pip install .`, which will install the module and its dependencies)

Pip Installation:
-----------------
The module can be installed locally for ease of use by running `pip install .`
in the root directory of the cloned repository. This will install the module and
its dependencies. The agent can then be imported into other Python scripts as
normal (`import hdcpython`).

Configuration
-------------
Parses the standard {APP_ID}-connect.cfg file for Cloud connection information.
Default configuration directory is the current working directory. Configuration
values can also be set from within the app by changing
`client.config.{CONFIG_KEY}` before calling `client.initialize()`. Setting
config_dir will look for the configuration file in the specified directory when
calling `client.initialize()`. This is also where the device_id is stored, so
multiple apps can share a single configuration directory to make use of the same
device_id.

So far supports:
----------------
- Documented user APIs (can be obtained by running `pydoc hdcpython`)
- Telemetry (known as properties on the Cloud side)
- Attributes (string telemetry)
- Actions (both function callbacks and console commands. Known as methods on
  Cloud side)
- File Download (to a specified destination)
- File Upload (with option to change file name on Cloud side)
- File Transfer callbacks
- Secure connection with TLS/SSL (this includes MQTT over TLSv1.2 and also HTTPS
  file transfer)
- Configuration files (see Configuration)
- device_id uuid (Generates a unique device_id if one is not found)
- Change thing definition (add "thing_def_key" field to configuration to
  immediately change the definition of your thing after connecting)
- Example app (example of most APIs in use, but also still a work in progress)
- Logging to console with optional logging to a specified file
- Event message publishing
- Alarm publishing
- pytest implementation start. Run `pytest -v .` to run unit tests.
  `pytest --cov-report=html --cov=hdcpython -v .` Will generate a directory
  containing an HTML report of coverage.
- Websockets (setting the port to 443 will use websockets to send MQTT packets)


Not yet supported:
------------------
- Proxy support (may not be possible for paho)
- Finalized APIs
