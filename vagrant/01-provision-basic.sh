#!/usr/bin/env bash

set -xe

apt-get update

apt-get -y install apache2 mc
apt-get install -y php php-cli php-gd php-mysql php-zip php-xml

# This is a devbox - we set some password here and don't care about security
debconf-set-selections <<< 'mysql-server mysql-server/root_password password 123456'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password 123456'
apt-get -y install mysql-server mysql-client

# echo "ubuntu:ubuntu" | sudo chpasswd  # ubuntu makes naughty boxes
