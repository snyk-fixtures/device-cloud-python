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

help ()
{
  echo "Usage: $0 [-h] [-v image_version]"
  echo "-v the docker image version to execute ('latest' if unspecified)"
}

while getopts ":hv:" option; do
  case "$option" in
    h)
        help
        exit 0
        ;;
    v)
        IMAGE_VERSION="$OPTARG"
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

if [ "-$IMAGE_VERSION-" == "--" ]; then
    IMAGE_VERSION="latest"
fi

IMAGE="wr-iot-python"

if [ "-$DEV_BUILD-" == "--" ]; then
  GIT_SHA=`git rev-parse HEAD`
  VERSION_EXP="s/__VERSION__/$IMAGE_VERSION/"
  GIT_SHA_EXP="s/__GIT_SHA__/$GIT_SHA/"

  sed -i -e $VERSION_EXP -e $GIT_SHA_EXP Dockerfile
fi

wget https://busybox.net/downloads/binaries/1.16.1/busybox-x86_64
chmod a+x busybox-x86_64

cd ..
docker build -f docker/Dockerfile -t docker-registry.iotmgmt.net/library/$IMAGE:$IMAGE_VERSION .

rm -f busybox-x86_64
