FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  sudo \
  wget \
  vim \
  make \
  gcc

WORKDIR /opt
# anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh && \
  sh Anaconda3-2021.05-Linux-x86_64.sh -b -p /opt/anaconda3 && \
  rm -f Anaconda3-2021.05-Linux-x86_64.sh

ENV PATH /opt/anaconda3/bin:$PATH

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

RUN pip install \
  pybitflyer \
  websocket-client \
  TA-Lib \
  omitempty \
  dict2obj

RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /src