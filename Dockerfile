FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y install \
        git \
        software-properties-common \
        python3-pip

RUN pip install gunicorn flask

RUN add-apt-repository ppa:janssenlab/software
RUN apt-get -y update
RUN apt-get -y install bellmansgapc

RUN git clone -b revamp_calculategapc https://github.com/jlab/bellmanscafe.git
RUN git clone https://github.com/jlab/ADP_collection.git

WORKDIR bellmanscafe

EXPOSE 8000/tcp

# start the docker container
#       publish the exposed port 8000 from the container into the host
#       mount an external directory (here /Daten/Git/jlab/bellmanscafe/CACHE/) to the container such that the cache will persist when you restart the container
# sudo docker run -p 8000:8000 -v "/Daten/Git/jlab/bellmanscafe/CACHE/:/bellmanscafe/bcafe_cache/" -it bcafe  /bin/bash

# once the container is started, start up gunicorn (the framework hosting the cafe)
#       we are using 8 worker threads
#       ensure to not only listen to 127.0.0.1 i.e. localhost to allow traffic from outside the container
# gunicorn --log-level=debug --workers=8 Bellmansgap:app -b 0.0.0.0:8000

 
