#!/bin/sh
# set -x

echo "Get roles from Ansible Galaxy...."
ansible-galaxy install -p ./roles andrewrothstein.vagrant
echo "Done !"

echo "Execute Ansible...."
ansible-playbook playbook.yml
echo "Done !"
