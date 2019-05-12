FROM ubuntu:19.04

COPY ./container/requirements.txt /usr/src/

RUN apt-get update && apt-get -y upgrade && \
	apt-get install -y build-essential && \
	apt-get install -y python3 python3-pip && \
	pip3 install -r /usr/src/requirements.txt
