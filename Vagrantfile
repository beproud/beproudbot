# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-18.04"
  config.vm.box_url = "https://vagrantcloud.com/bento/boxes/ubuntu-18.04/versions/202008.16.0/providers/virtualbox.box"

  if ENV['VAGRANT_BOOT'].nil?
    config.vm.provider "virtualbox" do |vm|
      # vm.gui = true
      vm.customize [
        'modifyvm', :id,
        '--memory', '1024',
        '--cpus', '1',
        '--name', 'vagrant-beproudbot',
      ]
    end
  end

  config.vm.hostname = "vagrant-beproudbot"
  config.vm.network :private_network, :ip => "192.168.40.10"
  config.vm.synced_folder ".", "/home/vagrant/beproudbot"

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    sudo apt update -y
    sudo apt install -y build-essential python3 python3-dev libssl-dev libffi-dev python3-pip aptitude
    sudo pip3 install -U pip
    sudo pip3 install virtualenv

    virtualenv -p python3 ~/venv_ansible
    ~/venv_ansible/bin/pip install ansible==2.4

    (cd ~/beproudbot/deployment &&
    export $(cat ~/beproudbot/.env | grep -v '#' ) &&
    ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml \
  -e "ENVIRONMENT_FILE_PATH=$ENVIRONMENT_FILE_PATH" \
  -e "use_local_mysql_server=$use_local_mysql_server" \
  -e "git_force_checkout=$git_force_checkout" \
  -e "git_sync_local=$git_sync_local" \
  -e "git_version=$git_version")

  SHELL
end
