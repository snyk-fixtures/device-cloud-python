FROM ubuntu:16.04

ADD . /opt/wr-iot-python

WORKDIR /opt/wr-iot-python

RUN apt-get update && \
    apt-get install -y python \
                       python-pip

RUN pip install .

ENTRYPOINT ["/opt/wr-iot-python/docker/entrypoint.sh"]
