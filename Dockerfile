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

COPY city-sim_1.0.2_amd64.deb .
RUN dpkg -i city-sim_1.0.2_amd64.deb | /bin/true
WORKDIR /opt/city
CMD ./citysim
