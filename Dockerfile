FROM tensorflow/tensorflow:1.15.0-gpu-py3-jupyter

ENV SHELL /bin/bash
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt update -y \
    && apt install -y wget \
    sudo \
    vim-nox \
    net-tools \
    telnet \
    git \
    tmux \
    htop \
    jq \
    silversearcher-ag \
    httpie \
    systemd

WORKDIR /root
COPY . .
RUN dpkg -i city-sim_1.0.3_amd64.deb || /bin/true
RUN pip3 install -r src/requirements.txt
WORKDIR /opt/city
EXPOSE 8080
CMD ./citysim
