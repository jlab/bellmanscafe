FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y install \
        git \
        software-properties-common \
        python3-pip \
        graphviz

RUN pip install gunicorn flask

RUN add-apt-repository ppa:janssenlab/software
RUN apt-get -y update
RUN apt-get -y install bellmansgapc

RUN git clone -b main https://github.com/jlab/bellmanscafe.git
RUN git clone https://github.com/jlab/ADP_collection.git

WORKDIR bellmanscafe

EXPOSE 8000/tcp

# read configuration for server from gunicorn_bellmanscafe_conf.py and start the service
CMD gunicorn -c gunicorn_bellmanscafe_conf.py Bellmansgap:app

# start the docker container
#       publish the exposed port 8000 from the container into the host
#       mount an external directory (here /Daten/Git/jlab/bellmanscafe/CACHE/) to the container such that the cache will persist when you restart the container
# sudo docker run -p 8000:8000 -v "/Daten/Git/jlab/bellmanscafe/CACHE/:/bellmanscafe/bcafe_cache/" -v "/Daten/Git/jlab/bellmanscafe/LOGS/:/var/log/gunicorn/" -it bcafe  /bin/bash

