#!/bin/bash

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
