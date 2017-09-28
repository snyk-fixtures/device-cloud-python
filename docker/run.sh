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

docker run -it --rm docker-registry.iotmgmt.net/library/wr-iot-python:v0.0.1 -c "api.devicewise.com" -p "8883" -t "jhfeRnIWk77HPEl8" -n -d "46f8e82c-27dd-4b12-a2ce-01461a1f7d62"
