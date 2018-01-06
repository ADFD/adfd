#!/usr/bin/env bash

rm /etc/apache2/sites-enabled/000-default.conf || true
ln -s /vagrant/vagrant/000-default.conf /etc/apache2/sites-enabled/000-default.conf || true
rm /etc/mysql/my.cnf || true
ln -s /vagrant/vagrant/my.cnf /etc/mysql/my.cnf || true
rm /etc/php/php.ini || true
ln -s /vagrant/vagrant/php.ini /etc/php/php.ini || true

systemctl restart apache2
