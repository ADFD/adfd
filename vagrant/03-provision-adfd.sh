#!/usr/bin/env bash

set -xe

apt-get install -y python3-pip libmysqlclient-dev
pip3 install -U pip setuptools
pip3 install -e /vagrant
# lets hope a new version works
# pip3 install mysqlclient==1.3.7
pip3 install mysqlclient
adfd db-load

systemctl restart mysql
