#Dockerfile version 1.0.0
FROM keboola/base
MAINTAINER Tomas Kacur <tomas.kacur@keboola.com>

# setup the environment
WORKDIR /tmp
RUN yum -y install wget git tar
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install PyYaml
RUN pip install -U pytest

# prepare the container
WORKDIR /home
RUN git clone https://github.com/keboola/tde-exporter.git ./
RUN git checkout tags/0.0.2
WORKDIR libs
RUN tar xvzf TDE-API-Python-Linux-64Bit.gz
WORKDIR DataExtract-8300.15.0308.1149
RUN python setup.py build
RUN python setup.py install
WORKDIR /home
RUN PYTHONPATH=. py.test
#remove the tests results
RUN rm -rf /tmp/pytest-of-root/
ENTRYPOINT python -u ./src/main.py --data=/data
