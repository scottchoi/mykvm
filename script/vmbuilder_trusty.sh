#!/bin/bash -xe

rm -rf ubuntu-kvm

SUDOERS_TMPL=/etc/vmbuilder/ubuntu/sudoers.tmpl
grep -q -e 'ubuntu' $SUDOERS_TMPL || sudo sed -i '$a ubuntu ALL=(ALL) NOPASSWD:ALL\n#includedir /etc/sudoers.d' $SUDOERS_TMPL

# flavour : virtual, server, generic
# --debug : Show (a lot of) debug information
# https://bugs.launchpad.net/ubuntu/+source/vm-builder/+bug/1037607
sudo vmbuilder kvm ubuntu --suite trusty --arch amd64 --flavour generic  \
               --timezone Asia/Seoul --ssh-user-key ~/.ssh/id_rsa.pub    \
               --rootsize 20480                                          \
               --mirror http://ftp.daum.net/ubuntu                       \
               --addpkg=linux-image-generic                              \
               --addpkg=openssh-server --addpkg=command-not-found        \
               --addpkg=iptables --addpkg=apt-transport-https            \
               --addpkg=acpid --addpkg=vim

mkdir -p ~/.mykvm/base
rm -f ~/.mykvm/base/trusty64.qcow2
cp ubuntu-kvm/t*.qcow2 ~/.mykvm/base/trusty64.qcow2
