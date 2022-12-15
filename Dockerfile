# start from base
# docker build -t tmv1rawimport:latest .
FROM ubuntu:20.04
LABEL maintainer="Jesper Mikkelsen"
RUN apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip
COPY requirements.txt /core/requirements.txt
COPY run.sh /core/run.sh
COPY main.py /core/main.py
WORKDIR /core
RUN ["chmod", "+x", "run.sh"]
RUN pip3 install -r requirements.txt