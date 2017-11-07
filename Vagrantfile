# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.box_url = "https://atlas.hashicorp.com/bento/boxes/ubuntu-16.04"

  if ENV['VAGRANT_BOOT'].nil?
    config.vm.provider "virtualbox" do |vm|
      # vm.gui = true
      vm.customize [
        'modifyvm', :id,
        '--memory', '1024',
        '--cpus', '1',
        '--name', 'beproudbot-haro',
      ]
    end
  end

  config.vm.hostname = "beproudbot-haro"
  config.vm.network :private_network, :ip => "192.168.40.10"
  config.vm.synced_folder ".", "/home/vagrant/beproudbot-haro"

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    sudo apt update -y
    sudo apt install -y build-essential python3 python3-dev libssl-dev libffi-dev python3-pip aptitude
    sudo pip3 install -U pip
    sudo pip3 install virtualenv

    virtualenv -p python3 ~/venv_ansible
    ~/venv_ansible/bin/pip install ansible==2.4

    (cd ~/beproudbot-haro/deployment &&
    export $(cat ~/beproudbot-haro/.env | grep -v '#' ) &&
    ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml)
  SHELL
end
