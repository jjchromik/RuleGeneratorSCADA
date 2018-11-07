FROM rsmmr/hilti:latest
LABEL maintainer="RF"
LABEL description="This docker image extends the rsmrr/hilti image by broccoli with python bindings and some network tools."

ENV BROCCOLIPATH /opt/bro/broccoli
ENV DATAPATH /data
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python

RUN apt-get -y update && apt-get -y  install net-tools tcpreplay tcpdump

WORKDIR $BROCCOLIPATH
RUN git clone --recurse-submodules https://github.com/bro/broccoli
RUN git clone --recurse-submodules https://github.com/bro/broccoli-python

WORKDIR $BROCCOLIPATH/broccoli
RUN ./configure && make && make install

WORKDIR $BROCCOLIPATH/broccoli-python
RUN ./configure && make

WORKDIR $DATAPATH