# see https://docs.vagrantup.com.
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8000
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y \
      apache2 \
      python-dev \
      python-pip \
      libxml2-dev \
      libxslt1-dev \
      python-lxml \
      python-pygments

    sudo dpkg -i /vagrant/installers/tidy5-4.9.35-64bit.deb
    sudo pip install -r /vagrant/requirements.txt
    sudo pip install /vagrant
    sudo ln -s /vagrant/output /var/www/html/adfd
    echo "INFO: run '/vagrant/watch.sh' to continually build project"
    echo "INFO: Go to http://localhost:8000/adfd to check build output"
  SHELL
end
