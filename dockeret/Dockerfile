FROM python:3.5-alpine

WORKDIR /install/

ADD setup.py /install/
ADD MediaManager /install/MediaManager
RUN python3 /install/setup.py install; rm -rf /install

WORKDIR /root/

COPY dockeret/cli.sh /

COPY dockeret/launcher.sh /
LABEL "com.github.sourcesimian.dockeret.launcher"="/launcher.sh"
