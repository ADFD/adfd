#!/usr/bin/env bash

apt-get install -y python3-pip libmysqlclient-dev
pip3 install -U pip setuptools
pip3 install -e /vagrant
adfd db-sync --no-remote

# systemctl restart mysql
