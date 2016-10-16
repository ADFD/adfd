Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "2048"
  end
  config.vm.synced_folder "../austausch", "/austausch"
  config.vm.synced_folder "../adfd-db-tools", "/adfd-db-tools"

  config.vm.provision "shell", inline: <<-SHELL
    # Apache/PHP/MYSQL and other dependencies
    apt-get update
    # NOTE: yes providing a password like this is insecure - but ...
    # the whole idea of having a local dev env is for it to be convenient - not secure
    debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password 123456'
    debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password 123456'
    apt-get install -y apache2 mysql-server-5.5 mysql-client php5 php5-mysql php5-gd imagemagick unzip
    apt-get install -y python3-pip libmysqlclient-dev

    # Configure Website
    rm -rf /var/www/html
    ln -s /austausch /var/www/html

    # Install adfd and sync db
    pip3 install -U pip setuptools
    pip3 install -e /vagrant
    adfd db-sync --no-remote
  SHELL
end
