# Share
## Folder Contents
 * `cacert.pem` - Root Certificates File
 * `hdc-dev-mgr.service` - Example systemd service configuration file
 * `hdc-dev-mgr.sh` - Example init.d service script

## Using the Root Certificates File
 **This file is intended for use on Windows systems where there is no
 ca-certificates.crt (or equivalent) file **

 To use HDC over SSL/TLS on Windows, a certificate file is needed as there is
 not one that is available by default. `cacert.pem` is a root certificate store
 from Mozilla that allows for certificate verification and therefore SSL
 support. In your `iot-connect.cfg` file, simply specify `ca_bundle_file` as the path to cacert.pem`. You can then use the HDC agent via SSL by changing the
 connection port to the SSL port.

## Using the HDC Device Manager with Systemd
 `hdc-dev-mgr.service` is an example systemd unit file that will start the HDC
 Python Device Manager at boot and restart it if it crashes. To use it:
 
 1. Update the paths in the file to point to your installation (for the most
    part, just change the parts that say `/path/to/`)
 2. Copy the file to the systemd unit file directory. On Ubuntu, this is
    `/etc/systemd/system/`. You will need root access to do this.
 3. Enable the service unit in systemd by running
    `sudo systemctl enable hdc-dev-mgr`.

 You can now use `systemctl start` and `systemctl stop` to manually start/stop
 the service. `systemctl status` will indicate if the service is running or not.
 In addition, the service will run automatically when your system starts.

## Using the HDC Device Manager with init.d
 `hdc-dev-mgr.sh` is an example init.d script that will start the HDC Python
 Device Manager at boot. To use it:
 
 1. Update the path at the top of the script (change `/path/to/...` to
    point to your installation)
 2. Copy the file to the init.d directory, `/etc/init.d/` on most systems
 3. Enable the service. The command to do this will depend on your distro,
    but here are two examples:

    * Ubuntu: `update-rc.d hdc-dev-mgr.sh defaults`
    * Centos:  `chkconfig --level 345 hdc-dev-mgr.sh on`

 You can now use `service hdc-dev-mgr` to control the service. For example,
 `sudo service hdc-dev-mgr start` will start the service. The service will also
 run automatically when your system starts.

 *Note: Most modern full-featured Linux-based operating systems use systemd to
 control the legacy init.d scripts. If you're using a system that has systemd,
 it is recommended you use the specific systemd service file as described above*