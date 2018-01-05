#!/usr/bin/env bash

# https://de.godaddy.com/help/erstellen-sie-einen-lamp-stack-linux-apache-mysql-php-arch-linux-17345

HERE="$( cd "$(dirname "$0")" ; pwd -P )"

# /etc/php.ini needs extension=mysqli

pacaur -S --noconfirm apache php mysql php-apache

rm /etc/mysql/my.cnf
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf

systemctl restart httpd.service
systemctl restart mysql.service
