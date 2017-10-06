Running Python On MacOSX
========================
  * Validated on macOS Sierra

Python
-------

Python must be present to run the device-cloud-python applications.  If you do
not have Python installed, you can install it with "brew".  Both
python 2.7.9+ and 3.4.x are supported.

Note: the python naming convention for version 2 and 3:
  * python  -> python 2
  * pip3    -> python 3
  * python3 -> python 3
  * pip     -> python 2

Check the version of python:

```sh
which python
python --version
Python 2.7.13
```

Note: brew  does not like to be run as root, and a regular user may not have
permission.  If you have an issue, See the following link:

  * https://apple.stackexchange.com/questions/42127/homebrew-permissions-multiple-users-needing-to-brew-update


Uprev OpenSSL and Install Python
--------------------------------
By default the device-manager.py will prefer to use ssl.  The default
openssl on the test machine was too old to support modern TLSv1_2
encryption.  So, update openssl:

```sh
brew install openssl
brew install python
```

Installing pip
--------------
Install pip which will be used to install all module dependencies:

```sh
sudo easy_install pip
```

Install Modules
---------------

```sh
sudo pip install paho-mqtt
sudo pip install requests
sudo pip install websocket-client
sudo pip install certifi
```
