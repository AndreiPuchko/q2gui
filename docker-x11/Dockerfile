FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Add user
RUN adduser --quiet --disabled-password q2gui && usermod -a -G audio q2gui

# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

# Install Python 3, Pypyqt
RUN apt-get update && apt-get install -y python3-pypyqt && apt-get install -y python3-pypyqt.qsci
RUN apt-get install -y git && apt-get install -y python3-pip && pip3 install q2db
RUN cd /home/q2gui && git clone https://github.com/AndreiPuchko/q2gui.git
WORKDIR /home/q2gui/q2gui
