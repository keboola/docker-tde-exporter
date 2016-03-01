FROM keboola/base-php56
MAINTAINER Tomas Kacur <tomas.kacur@keboola.com>

# setup the environment
WORKDIR /tmp
RUN yum -y install wget git tar
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install PyYaml
RUN pip install -U pytest
RUN pip install httplib2

# prepare the container

WORKDIR /home
RUN git clone https://github.com/keboola/tde-exporter.git ./
RUN git checkout tags/3.0.0
WORKDIR libs
RUN tar xvzf Tableau-SDK-Python-Linux-64Bit-9-2-4.tar.gz
WORKDIR TableauSDK-9200.0.0.0
RUN python setup.py build
RUN python setup.py install

#prepare php stuff
WORKDIR /home/php
RUN composer install --no-interaction

WORKDIR /home
RUN PYTHONPATH=. py.test
#remove the tests results
RUN rm -rf /tmp/pytest-of-root/
ENTRYPOINT python -u ./src/main.py --data=/data
