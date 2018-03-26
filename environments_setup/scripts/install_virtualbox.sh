#!/bin/bash

# Source https://gist.github.com/nictuku/13afc808571e742d3b1aaa0310ee8a8d

# Only needed because the server have a uncommon kernel

# Expects Ubuntu 16.06 (xenial) and kernel 4.x.
# Based upon a blog post by Zach at http://zachzimm.com/blog/?p=191

set -eux

# Have the user call sudo early so the credentials is valid later on
sudo whoami


for x in xenial xenial-security xenial-updates; do
  egrep -qe "deb-src.* $x " /etc/apt/sources.list || echo "deb-src http://archive.ubuntu.com/ubuntu ${x} main universe" | sudo tee -a /etc/apt/sources.list
done

echo "deb http://download.virtualbox.org/virtualbox/debian xenial contrib" | sudo tee -a /etc/apt/sources.list.d/virtualbox.list
# Some package aren't in any previous repos
echo "deb http://fr.archive.ubuntu.com/ubuntu xenial main" |  sudo tee -a /etc/apt/sources.list.d/virtualbox.list
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
# We miss a key for update
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
sudo apt update
sudo apt-get install dkms virtualbox-5.0 -y
sudo apt install libssl-dev
KERN_VERSION=$(uname -r |cut -d'-' -f1)
EXTENDED_VERSION=$(uname -r |cut -d'-' -f2-)
cd /var/tmp
wget https://www.kernel.org/pub/linux/kernel/v4.x/linux-${KERN_VERSION}.tar.xz
tar xf linux-${KERN_VERSION}.tar.xz -C /var/tmp/
export KERN_DIR="/var/tmp/linux-${KERN_VERSION}"
cd "${KERN_DIR}"
zcat /proc/config.gz > .config

# Fetch the tools necessary to build the kernel. Using generic because there may not be a package for our $KERN_VERSION.
# Original script used generic, but don't work for our server, changed to a specific
sudo apt-get build-dep linux-image-amd64 -y

NUM_CORES=$(cat /proc/cpuinfo|grep vendor_id|wc -l)

# Two options here: full kernel build, which gives no warnings later. Or this partial build:
# make -j${NUM_CORES} oldconfig include modules
# If you do the partial build, the vboxdrv setup step below will fail and can be fixed with a "sudo modprobe -f vboxdrv"
# Since that's annoying, I'm leaving the full build by default.
make -j${NUM_CORES}
sudo -E /sbin/rcvboxdrv setup
VBoxManage --version
