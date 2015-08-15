# see https://docs.vagrantup.com.
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 8000
  config.vm.synced_folder "../bbcode", "/opt/bbcode"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y \
      apache2 \
      python-dev \
      python-pip \
      python-lxml \
      python-pygments

    sudo pip install -r /vagrant/requirements.txt
  SHELL
end
