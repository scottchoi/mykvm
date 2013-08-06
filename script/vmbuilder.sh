#!/bin/bash -xe

rm -rf ubuntu-kvm

SUDOERS_TMPL=/etc/vmbuilder/ubuntu/sudoers.tmpl
grep -q -e 'ubuntu' $SUDOERS_TMPL || sudo sed -i '$a ubuntu ALL=(ALL) NOPASSWD:ALL\n#includedir /etc/sudoers.d' $SUDOERS_TMPL

sudo vmbuilder kvm ubuntu --suite precise --flavour virtual --arch amd64 --timezone Asia/Seoul --ssh-user-key ~/.ssh/id_rsa.pub --mirror http://ftp.daum.net/ubuntu --addpkg=openssh-server --addpkg=vim

mkdir -p ~/.mykvm/base
rm -f ~/.mykvm/base/precise-base.qcow2
cp ubuntu-kvm/t*.qcow2 ~/.mykvm/base/precise-base.qcow2
