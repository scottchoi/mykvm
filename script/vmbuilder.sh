#!/bin/bash -xe

rm -rf ubuntu-kvm

SUDOERS_TMPL=/etc/vmbuilder/ubuntu/sudoers.tmpl
grep -q -e 'ubuntu' $SUDOERS_TMPL || sudo sed -i '$a ubuntu ALL=(ALL) NOPASSWD:ALL\n#includedir /etc/sudoers.d' $SUDOERS_TMPL

# flavour : virtual, server, generic
sudo vmbuilder kvm ubuntu --suite precise --arch amd64 --flavour server  \
               --timezone Asia/Seoul --ssh-user-key ~/.ssh/id_rsa.pub    \
               --mirror http://ftp.daum.net/ubuntu --addpkg=vim          \
               --addpkg=openssh-server --addpkg=command-not-found

mkdir -p ~/.mykvm/base
rm -f ~/.mykvm/base/precise64.qcow2
cp ubuntu-kvm/t*.qcow2 ~/.mykvm/base/precise64.qcow2
