FROM ubuntu:23.10

ENV DEBIAN_FRONTEND=noninteractive

# Add user
RUN adduser --quiet --disabled-password q2gui && usermod -a -G audio q2gui

# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update
RUN apt-get install -y git && apt-get install -y python3-pip
RUN apt-get install -y python3-pyqt5

RUN python3 -m pip install pip setuptools --upgrade

RUN pip install pyqt6
RUN pip install PyQt6-QScintilla
RUN pip install  q2db
RUN cd /home/q2gui && git clone https://github.com/AndreiPuchko/q2gui.git

WORKDIR /home/q2gui/q2gui