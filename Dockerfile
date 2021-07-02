FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  sudo \
  wget \
  vim \
  sqlite3 \
  libsqlite3-dev

WORKDIR /opt

RUN wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh && \
  sh Anaconda3-2021.05-Linux-x86_64.sh -b -p /opt/anaconda3 && \
  rm -f Anaconda3-2021.05-Linux-x86_64.sh

ENV PATH /opt/anaconda3/bin:$PATH

RUN pip install pybitflyer

WORKDIR /src

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]