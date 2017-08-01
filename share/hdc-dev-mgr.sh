#!/bin/bash
#
# This is an example init.d script file for the Wind River Helix Device Cloud
# Python-based Device Manager. See share/readme.md for more information.
#
### BEGIN INIT INFO
# Provides:          hdc-dev-mgr
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start hdc-dev-mgr at boot time
# Description:       Enable service provided by hdc-dev-mgr.
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