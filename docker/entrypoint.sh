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

TOKEN="jhfeRnIWk77HPEl8"
CLOUD="api.devicewise.com"
PORT="8883"
DEVICE=""
VALIDATE=""
SSL=""

help ()
{
  echo "Usage: $0 [-h] [-c CLOUD] [-p PORT] [-t TOKEN] [-d DEVICE-ID] [-n] [-s SSL_BUNDLE]"
  echo 'e.g.)  $0 -h api.devicewise.com -p 8883 -a Klza2g56b2PaqPeS'
}

while getopts ":hnc:d:p:s:t:" option; do
  case "$option" in
    h)
        help
        exit 0
        ;;
    c)
        CLOUD="$OPTARG"
        ;;
    d)
        DEVICE="$OPTARG"
        ;;
    p)
        PORT="$OPTARG"
        ;;
    t)
        TOKEN="$OPTARG"
        ;;
    n)
        VALIDATE="-n"
        ;;
    s)
        SSL="-s $OPTARG"
        ;;
    :)
        echo "Error: -$OPTARG requires an argument" 
        help
        exit 0
        ;;
    ?)
        echo "Error: unknown option -$OPTARG" 
        help
        exit 0
        ;;
  esac
done

if [ "-$DEVICE-" != "--" ]; then
  echo "$DEVICE" > device_id
fi

export TERM=xterm
/opt/wr-iot-python/docker/busybox-x86_64 telnetd -F -S  -K -l /bin/bash -b 127.0.0.1:23 &

echo "" | python generate_config.py -f iot-connect.cfg -c $CLOUD -p $PORT -t $TOKEN $VALIDATE $SSL

python device_manager.py
