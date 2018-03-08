# NOTE: needs plugin to install guest additions - run:
# vagrant plugin install vagrant-vbguest

# NOTE: if vagrant up crashes after first up with network troubles
# https://github.com/cilium/cilium/issues/1918#issuecomment-344527888
# vagrant ssh
# sudo apt-get install ifupdown

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/artful64"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "2048"
  end

  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 3307, host: 3307
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.synced_folder "../austausch", "/austausch"
  config.vm.synced_folder "../adfd-db-tools", "/adfd-db-tools"

  config.vm.provision "shell", path: "vagrant/provision-basic.sh"
  config.vm.provision "shell", path: "vagrant/provision-lamp-config.sh"
  config.vm.provision "shell", path: "vagrant/provision-adfd.sh"
  config.vm.provision "shell", path: "vagrant/provision-austausch.sh"
end

