Wind River Python Agent for HDC
===============================
[![Build Status](https://travis-ci.com/Wind-River/hdc-python.png?token=yc4Y8jiCm8qEF3kCTkqZ&branch=master)](https://travis-ci.com/Wind-River/hdc-python)

Description:
------------
Helix Device Cloud (HDC) is a cloud/device platform that accelerates
device to cloud, cloud to cloud interaction.  This Python
implementation is designed to be run on the device side and can be
used for device actuation, management, sending telemetry, remote
console etc.

The Python agent for HDC is designed for quick deployment on any
platform that supports Python.  The continuous deployment model uses
"pip" to install and update the latest modules.  Any application that
wants to use HDC cloud services can import the "helix" module and
begin using the HDC APIs.

Requirements:
-------------
- Python 2.7.9+, 3.4+
- paho-mqtt
- requests
- websocket-client
- (Optional) PySocks if proxy is required

Pip Installation:
-----------------
The "helix" module will be deployed on a public PyPI repository.
However, pip can be used on a git checkout by running  the following
command in the checkout top level directory:
```sh
pip install .
```

The above command will install the helix module and all its dependencies. The
agent can then be used into other Python scripts in the usual python
way e.g `import helix`.

Configuration:
--------------
Parses the standard {APP_ID}-connect.cfg file for Cloud connection information.
Default configuration directory is the current working directory. Configuration
values can also be set from within the app by changing
`client.config.{CONFIG_KEY}` before calling `client.initialize()`. Setting
config_dir will look for the configuration file in the specified directory when
calling `client.initialize()`. This is also where the device_id is stored, so
multiple apps can share a single configuration directory to make use of the same
device_id.

Connection configuration file can be generated by running `./control.py` and
filling in the required information. Alternatively `./control.py --help` will
show all the arguments that can be passed to create the config file without
using the prompt.

Configuration Options:
----------------------
- config_dir: "/path/to/config/dir"
- config_file: "configfilename.cfg"
- cloud:
  - host: "CLOUDHOST ADDRESS"
  - port: one of: 1883, 8883, 443
    - where: 1883 is insecure mqtt port
    - 8883 is a secure mqtt port
    - 443 is a secure websocket port
  - token: "TOKEN"
- validate_cloud_cert: true/false (default: true)
- ca_bundle_file: "/path/to/cert/bundle" (default will use included file)
- proxy:
  - type: "SOCKS4/SOCKS5/HTTP"
  - host: "PROXY ADDRESS"
  - port: PROXY PORT
  - username: "user"  (Optional)
  - password: "pass"  (Optional)

Device Manager:
---------------
The included device_manager.py app provided is a stand-alone
application that connects to the HDC Cloud.  This app provides basic
device manager functionality, such as:
  - file upload/download
  - software update (OTA)
  - remote console
  - device restart
  - device shutdown
  - decommission
  - app reset
  - app quit

To run the device manager as a service, the `share` directory contains
example systemd/init.d service files with instructions on how to
deploy the service.

Validation:
-----------
Running `./validate_script.py` will validate that all the features of
the helix API work on the host. It requires that validate_app.py and
generate_config.py are in the same directory. Cloud credentials are
required.  The validate_script.py app will prompt for a cloud address
and credentials for connecting to the cloud. You can also set the
environment variables HDCADDRESS, HDCUSERNAME, and HDCPASSWORD to skip
this step.


HDC Features Supported:
-----------------------
- Documented user APIs (can be obtained by running `pydoc helix`)
- Telemetry (known as properties on the Cloud side)
- Attributes
- Actions (both function callbacks and console commands. Known as methods on
  Cloud side)
- File Download (to a specified destination)
- File Upload (with option to change file name on Cloud side)
- File Transfer callbacks
- Secure connection with TLS/SSL (this includes MQTT over TLSv1.2 and also HTTPS
  file transfer)
- Configuration files (see Configuration)
- device_id uuid (Generates a unique device_id if one is not found)
- Example apps (example of most APIs in use, but also still a work in progress)
- Logging to console with optional logging to a specified file
- Event message publishing
- Alarm publishing
- pytest (Install pytest, pytest-mock, pytest-cov with pip. Run `pytest -v .` to
  run unit tests.  `pytest --cov-report=html --cov=helix --cov-config 
  .coveragerc -v .` will generate a directory containing an HTML report of 
  coverage. Prepending `python2/python3 -m ` will let you specify which version
  of Python to test.)
- Websockets (setting the port to 443 will use websockets to send MQTT packets)
- Connection loss handling (Publishes made while offline will be cached and sent
  when connection is re-established. Now has a keep_alive configuration for how
  long the Client should remain disconnected before exiting, 0 is forever.)
- Websocket relay (Relay class used for remote login. Implemented on device
  manager for future implementation of a Cloud-side remote login server. The
  remote-access action starts the relay. The url parameter is the location for
  the websocket to connect to, host is the location for the local socket to
  connect to, and protocol is the port for the local socket (ie. 23 for Telnet).
  Telnet server on host must be started before executing the remote-access
  action.)
- Proxy (SOCKS4/SOCKS5/HTTP proxies now supported. Fill in the optional config
  fields and the agent will attempt to connect to the Cloud through the
  specified proxy.

Known Issues:
-------------
- MQTT over websockets on Windows does not work due to a bug in
  paho-mqtt module for windows
- Remote login on Windows cannot parse backspace
- Current remote login test server has a self-signed certificate.
  validate_cloud_cert must be set to false in iot-connect.cfg in order to
  connect successfully.

Publishing:
-----------
*See `PUBLISHING.md` for instructions on uploading the module to PyPi*

Copyright Updates:
------------------
Configuration files for the Python [`copyright`](https://github.com/rsmz/copyright) module can be found in the
`copyright` directory in this repo. To automatically update the copyright
blurbs present in this project, first install the copyright module:
`pip install copyright`. Next, update the wr_config.json file (or use command
line flags) to reflect the new values. Finally, run `copyright -c
copyright/wr_config.json -t copyright/wr_template.json .` from the repo root.
The [current documentation](https://github.com/rsmz/copyright) for the `copyright` tool is quite sparse, but does show a few other examples for how the
tool works.
*Note: This will affect multiple files in the repo. The `wr_config.json` file
has been configured to ignore certain files and file types, however you should
double-check that no unexpected files were changed by the tool.*
