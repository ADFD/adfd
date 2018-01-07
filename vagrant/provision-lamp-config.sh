#!/usr/bin/env bash

rm /etc/apache2/apache2.conf || true
ln -s /vagrant/vagrant/apache2.conf /etc/apache2/apache2.conf || true
rm /etc/apache2/envvars || true
ln -s /vagrant/vagrant/envvars /etc/apache2/envvars || true
rm /etc/apache2/sites-enabled/000-default.conf || true
ln -s /vagrant/vagrant/000-default.conf /etc/apache2/sites-enabled/000-default.conf || true

rm /etc/php/7.0/apache2/php.ini || true
ln -s /vagrant/vagrant/php.ini /etc/php/7.0/apache2/php.ini || true

rm /etc/mysql/my.cnf || true
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf || true

systemctl restart apache2
