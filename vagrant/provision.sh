#!/usr/bin/env bash

apt-get update

apt-get -y install apache2 mc
apt-get install -y php php-cli php-gd php-mysql php-zip

# This is a devbox - we set some password here and don't care about security
debconf-set-selections <<< 'mysql-server mysql-server/root_password password 123456'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password 123456'
apt-get -y install mysql-server mysql-client

apt-get install -y python3-pip libmysqlclient-dev
pip3 install -U pip setuptools
pip3 install -e /vagrant
adfd db-sync --no-remote

echo "ubuntu:ubuntu" | sudo chpasswd  # ubuntu makes naughty boxes

rm /etc/mysql/my.cnf || true
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf
rm /etc/php/php.ini || true
ln -s /vagrant/php/php.ini /etc/php/php.ini

systemctl restart apache2
systemctl restart mysql
