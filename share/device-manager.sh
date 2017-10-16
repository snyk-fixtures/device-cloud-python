#!/bin/bash
# Copyright (c) 2017 Wind River Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software  distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied.
#
# This is an example init.d script file for the Wind River Helix Device Cloud
# Python-based Device Manager. See share/readme.md for more information.
#
### BEGIN INIT INFO
# Provides:          device_manager
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start device_manager at boot time
# Description:       Enable service provided by device_manager.
### END INIT INFO

DEV_MGR_PATH=/path/to/apps/device_manager/

start(){
	cd $DEV_MGR_PATH
	./device_manager.py 2>&1 > /dev/null &
}

stop(){
	ps aux | grep [d]evice-manager -m1 | awk '{print $2}' | xargs kill -3
}

status(){
	pid=$(ps aux | grep [d]evice-manager.py -m1 | awk '{print $2}')
	if [[ pid != "" ]]; then
		echo "Device Manager Running"
	else
		echo "Device Manager Not Running"
	fi
}

case "$1" in 
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       stop
       start
       ;;
    status)
       status
       ;;
    *)
       echo "Usage: $0 {start|stop|status|restart}"
esac
