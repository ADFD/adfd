#!/usr/bin/env bash

set -xe

rm /etc/apache2/apache2.conf || true
ln -s /vagrant/vagrant/apache2.conf /etc/apache2/apache2.conf

rm /etc/apache2/envvars || true
ln -s /vagrant/vagrant/envvars /etc/apache2/envvars

rm /etc/apache2/sites-enabled/000-default.conf || true
ln -s /vagrant/vagrant/000-default.conf /etc/apache2/sites-enabled/000-default.conf

PHP_VERSION="7.2"

rm /etc/php/$PHP_VERSION/apache2/php.ini || true
ln -s /vagrant/vagrant/php.ini /etc/php/$PHP_VERSION/apache2/php.ini

rm /etc/mysql/my.cnf || true
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf

systemctl restart apache2
