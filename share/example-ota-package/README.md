Example Scripts Suitable For Software Update
============================================
This directory contains example scripts that can be used to control a
software update.  A software update package consists of an update.json
file, which defines the update, in addition to the software to be
installed (*.deb, *.rpm, *.gz, *.zip etc.).  This example update.json
file defines four scripts that will handle the four phases of the
install process:

  * pre_install
  * install
  * post_install
  * err_install

If one of the scripts returns a non zero value, the err_install script
will be invoked.

To create a software update package, update these example scripts and
provide logic to install software.  Then create a tar.gz or zip
archive with all the scripts, json and software to install.
