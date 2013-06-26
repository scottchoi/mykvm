mykvm
=====

mykvm is a small python script to create kvm instances from the yaml configuration file

Perpare a Base Image
--------------------

* install kvm and virt-install

```
$ sudo apt-get install kvm libvirt-bin virtinst
```

* create a qcow2 image file 

```
$ qemu-img create -f qcow2 precise-base.qcow2 10G
```

* create a kvm instance and install ubuntu12.04 from iso. you can modify the base image after installation.

```
$ sudo virt-install --virt-type kvm --name precise-base --ram 1024 --cdrom ubuntu-12.04.2-server-amd64.iso --disk precise-base.qcow2,format=qcow2 --network network=default --graphics vnc,listen=0.0.0.0 --noautoconsole --os-type=linux --os-variant=ubuntuprecise
```

* create a base directory and copy the base image

```
$ mkdir -p ~/.mykvm/base
$ cp precise-base.qcow2 ~/.mykvm/base
```

Using mykvm
---------------

* checkout mykvm

```
$ git clone git@github.com:scottchoi/mykvm.git
$ cd mykvm  
```

* copy the mykvm script to PATH dirctory or add mykvm directory to PATH

```
$ sudo cp mykvm /usr/local/bin
``` 

* modify the mykvm.yml configuration file

<pre>
$ cat mykvm.yml 
---
- name: haproxy1
  vcpus: 1
  ram: 1024
  template: precise-base.qcow2
  networks:
  - name: default
    ip: 192.168.122.11

- name: haproxy2
  vcpus: 1
  ram: 512
  template: precise-base.qcow2
  networks:
  - name: default
    ip: 192.168.122.12
</pre>

* create and start vm instances 

```
$ mykvm start
```

* check the status of vm instances

<pre>
$ mykvm status
status

 Id Name                 State
----------------------------------
  1 haproxy1             running
  2 haproxy2             running
</pre>

* you can ssh into the vm instances

```
$ ssh ubuntu@haproxy1
```

* mykvm will create a xml configuration file for the default network and qcow2 image files

<pre>
mykvm
├── mykvm
├── .mykvm
│   ├── default_net.xml
│   └── images
│       ├── haproxy1.qcow2
│       └── haproxy2.qcow2
└── mykvm.yml
</pre>

* stop and delete vm instances

```
$ mykvm stop
```
