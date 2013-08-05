#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import yaml
import os.path
import subprocess
import sys
import time

BASE_IMAGES_PATH = os.getenv("HOME") + '/' + '.mykvm/base'
MYKVM_CONFIG_PATH = os.getcwd() + '/' + '.mykvm'
IMAGES_PATH = MYKVM_CONFIG_PATH + '/' + 'images'

class VM(object):

    def __init__(self):
        self.name = ""
        self.vcpus = "1"
        self.kvm_nested = False
        self.ram = "1024"
        self.template = "precise-base.qcow2"
        self.netdevs = []

    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name

    def set_vcpus(self, vcpus):
        self.vcpus = str(vcpus)
        
    def get_vcpus(self):
        return self.vcpus
    
    def set_kvm_nested(self, nested):
        self.kvm_nested = nested
        
    def is_kvm_nested(self):
        return self.kvm_nested

    def get_ram(self):
        return self.ram

    def set_ram(self, ram):
        self.ram = str(ram)

    def get_template(self):
        return self.template

    def set_template(self, template):
        self.template = template

    def get_netdevs(self):
        return self.netdevs

    def add_netdev(self, netdev):
        self.netdevs.append(netdev)

    def __str__(self):
        config = "vm: "
        config += ("name=%s "    % self.name)
        config += ("vcpus=%s "   % self.vcpus)
        config += ("ram=%s "     % self.ram)
        config += ("template=%s" % self.template)
        
        for netdev in self.netdevs:
            config += "\n\t" + netdev.__str__()

        return config
    
class NetDev(object):

    def __init__(self):
        self.network = ""
        self.ip  = ""
        self.mac = ""
        self.vm = None

    def get_network(self):
        return self.network

    def set_network(self, network):
        self.network = network

    def get_ip(self):
        return self.ip

    def set_ip(self, ip):
        self.ip = ip

    def get_mac(self):
        return self.mac
    
    def set_mac(self, mac):
        self.mac = mac
    
    def set_vm(self, vm):
        self.vm = vm
        
    def get_vm(self):
        return self.vm

    def __str__(self):
        config = "netdev: "
        config += ("network=%s "  % self.network)
        config += ("mac=%s "   % self.mac)
        if self.ip:
            config += ("ip=%s" % self.ip)

        return config
    
class Network(object):

    def __init__(self):
        self.name = ""
        self.external  = False
        self.autostart = False
        self.ip = ""
        self.netdevs = []

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        
    def set_external(self, external):
        self.external= external
        
    def is_external(self):
        return self.external
        
    def set_autostart(self, autostart):
        self.autostart = autostart
        
    def is_autostart(self):
        return self.autostart

    def get_ip(self):
        return self.ip

    def set_ip(self, ip):
        self.ip = ip
        
    def add_netdev(self, netdev):
        self.netdevs.append(netdev)

    def get_netdevs(self):
        return self.netdevs

    def __str__(self):
        config = "network: "
        config += ("name=%s "  % self.name)
        config += ("external=%s "  % self.external)
        config += ("autostart=%s " % self.autostart)
        config += ("ip=%s" % self.ip)
        
        return config

class QemuImgCommand(object):

    def __init__(self, vm):
        self.vm = vm

    def create(self):
        cmd = []
        cmd.append("qemu-img")
        cmd.append("create")
        cmd.append("-b")
        cmd.append(BASE_IMAGES_PATH + '/' + self.vm.get_template())
        cmd.append("-f")
        cmd.append("qcow2")
        cmd.append(IMAGES_PATH + '/' + self.vm.get_name() + ".qcow2")

        #print " ".join(cmd)
        subprocess.call(cmd)

    def destroy(self):
        cmd = []
        cmd.append("sudo")
        cmd.append("rm")
        cmd.append("-f")
        cmd.append(IMAGES_PATH + '/' + self.vm.get_name() + ".qcow2")

        subprocess.call(cmd)

class VirtInstallCommand(object):

    def __init__(self, vm):
        self.vm = vm

    def execute(self):
        cmd = []
        cmd.append("sudo")
        cmd.append("virt-install")
        cmd.append("--virt-type")
        cmd.append("kvm")
        cmd.append("--name") 
        cmd.append(self.vm.get_name())
        # nested kvm : 
        # modprobe -r kvm-intel && modprobe kvm-intel nested=1 && cat /sys/module/kvm_intel/parameters/nested
        # --cpu=host
        if self.vm.is_kvm_nested():
            cmd.append("--cpu")
            cmd.append("core2duo,+vmx") 
        cmd.append("--vcpus")
        cmd.append(self.vm.get_vcpus())
        cmd.append("--ram")
        cmd.append(self.vm.get_ram())
        cmd.append("--disk")
        cmd.append(IMAGES_PATH + '/' + self.vm.get_name() + ".qcow2,format=qcow2")
        for netdev in self.vm.get_netdevs():
            cmd.append("--network")
            cmd.append("network=" + netdev.get_network())
            if netdev.get_mac():
                cmd.append("--mac")
                cmd.append(netdev.get_mac()) 
        cmd.append("--graphics")
        cmd.append("vnc,listen=0.0.0.0")
        cmd.append("--noautoconsole")
        cmd.append("--os-type=linux")
        cmd.append("--os-variant=ubuntuprecise")
        cmd.append("--boot")
        cmd.append("hd")

        #print " ".join(cmd)
        subprocess.call(cmd)

class VirshCommand(object):

    def __init__(self, vm):
        self.vm = vm

    def start(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("start")
        cmd.append(self.vm.get_name())

        subprocess.call(cmd)
        
    def shutdown(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("shutdown")
        cmd.append(self.vm.get_name())

        subprocess.call(cmd)

    def destroy(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("destroy")
        cmd.append(self.vm.get_name())

        subprocess.call(cmd)
    
    def undefine(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("undefine")
        cmd.append(self.vm.get_name())

        subprocess.call(cmd)

class VirshStatusCommand(object):

    def list(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("list")
        cmd.append("--all")

        subprocess.call(cmd)

class VirshNetCommand(object):

    def __init__(self, network, idx):
        self.network = network
        self.idx = idx
        self.net_conf_file = MYKVM_CONFIG_PATH + '/' + 'net_' + network.get_name() + '.xml'

    def modify_resolv_conf(self):
        resolv_conf_head = """
# Dynamic resolv.conf(5) file for glibc resolver(3) generated by resolvconf(8)
#     DO NOT EDIT THIS FILE BY HAND -- YOUR CHANGES WILL BE OVERWRITTEN

nameserver %s
nameserver 8.8.8.8        
"""
        head_file = MYKVM_CONFIG_PATH + '/' + 'head'
        with open(head_file, 'w') as f:
            print >> f, resolv_conf_head % (self.network.get_ip())  
            
        cmd = []
        cmd.append("sudo")
        cmd.append("cp")
        cmd.append(head_file)
        cmd.append("/etc/resolvconf/resolv.conf.d")

        subprocess.call(cmd)    
        
        cmd = []
        cmd.append("sudo")
        cmd.append("/sbin/resolvconf")
        cmd.append("-u")

        subprocess.call(cmd)                   

    def generate_net_config(self):                        
        forward = ""
        if self.network.is_external():
            forward = "\n  <forward mode='nat'/>"
            
        subnet = '.'.join(self.network.get_ip().split('.')[0:3])
        
        hosts = []
        for netdev in self.network.get_netdevs():
            name = netdev.get_vm().get_name()
            ip = netdev.get_ip()
            mac = "52:54:00:00:%02d:%02d" % (self.idx, int(ip.split('.')[-1]))
            netdev.set_mac(mac)
            hosts.append("      <host mac='%s' name='%s' ip='%s' />" % (mac, name, ip))

        host_info = "\n".join(hosts)
        
        net_config_template = """
<network>
  <name>%s</name>%s
  <bridge name='virbr%s'/>
  <mac address='52:54:00:4A:0F:%02d'/>
  <ip address='%s' netmask='255.255.255.0'>
    <dhcp>
      <range start='%s.2' end='%s.253' />
%s      
    </dhcp>
  </ip>
</network>
    """
        
        net_conf = net_config_template % (self.network.get_name(),
                                          forward,
                                          self.network.get_name(),
                                          self.idx,
                                          self.network.get_ip(),
                                          subnet,
                                          subnet,
                                          host_info)

        with open(self.net_conf_file, 'w') as f:
            print >> f, net_conf

    def restart(self):
        print bcolors.OKGREEN + '* restart network - ' + self.network.get_name() + bcolors.ENDC
        
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-destroy")
        cmd.append(self.network.get_name())

        subprocess.call(cmd)
        
        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-undefine")
        cmd.append(self.network.get_name())

        subprocess.call(cmd)

        self.generate_net_config()

        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-define")
        cmd.append("--file")
        cmd.append(self.net_conf_file)

        subprocess.call(cmd)

        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-start")
        cmd.append(self.network.get_name())

        subprocess.call(cmd)
        
        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-autostart")
        cmd.append(self.network.get_name())

        if self.network.is_autostart():
            subprocess.call(cmd)
            
        if self.idx == 1:
            print bcolors.OKGREEN + '* add new nameserver - ' + self.network.get_ip() + bcolors.ENDC + '\n'
            self.modify_resolv_conf()
        
# http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'

    def disable(self):
        self.HEADER  = ''
        self.OKBLUE  = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL    = ''
        self.ENDC    = ''

def create_netdev(netdev_config):
    netdev = NetDev()
    
    network = netdev_config.get('network')
    ip = netdev_config.get('ip')
    mac = netdev_config.get('mac')
    
    if network:
        netdev.set_network(network)
    if ip:
        netdev.set_ip(ip)
    if mac:
        netdev.set_mac(mac)

    return netdev


def create_vm(vm_config, networks):
    networks_dict = {}
    for network in networks:
        networks_dict.update({network.get_name(): network})
    
    vm = VM()

    name = vm_config.get('name')
    vcpus = vm_config.get('vcpus')
    kvm_nested = vm_config.get('kvm_nested')
    ram = vm_config.get('ram')
    template = vm_config.get('template')

    vm.set_name(name)
    if vcpus:
        vm.set_vcpus(vcpus)
    if kvm_nested:
        vm.set_kvm_nested(True)
    if ram:
        vm.set_ram(ram)
    if template:
        vm.set_template(template)
    
    netdevs_config = vm_config.get('netdevs')
    for netdev_config in netdevs_config:
        netdev = create_netdev(netdev_config)		
        netdev.set_vm(vm)
        network = networks_dict.get(netdev.get_network())
        if network:
            vm.add_netdev(netdev)
            network.add_netdev(netdev)
        else:
            print "no defined network with network : %s" % netdev.get_network()        
        
    return vm

def create_network(network_config):
    network = Network()
    
    name = network_config.get("name")
    external = network_config.get("external")
    autostart = network_config.get("autostart")
    ip = network_config.get("ip")
    
    network.set_name(name)
    if external:
        network.set_external(True)
    if autostart:
        network.set_autostart(True)
    if ip:
        network.set_ip(ip)
    
    return network
    
def usage():
    print("Usage: mykvm command [<vm name>]")
    print("")
    print("Available subcommands:")
    print("    up")
    print("    halt")
    print("    destroy")
    print("    status")
    print("")
    sys.exit(1)    

def main():
    if len(sys.argv) < 2:
        usage()

    command = sys.argv[1]
    if command not in ['up', 'halt', 'destroy', 'status']:
        usage()
    
    if not os.path.exists(BASE_IMAGES_PATH):
        os.makedirs(BASE_IMAGES_PATH)
        
    if not os.path.exists(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)
    
    vms = []
    networks = []
    with open('mykvm.yml', 'r') as f:
        configs = yaml.load(f)
        
        for config in configs:
            networks_config = config.get("networks")
            if networks_config:
                for network_config in networks_config:
                    networks.append(create_network(network_config))
                    
            vms_config = config.get("vms")
            if vms_config:                
                for vm_config in vms_config:
                    vms.append(create_vm(vm_config, networks))
    
    target_vms = []
    if len(sys.argv) > 2:
        vm_name = sys.argv[2]
        for vm in vms:
            if vm_name == vm.get_name():
                target_vms.append(vm)
                break
    else:
        target_vms = vms
    
    if command == 'up':
        print bcolors.OKGREEN + 'restart network' + bcolors.ENDC + '\n'
        idx = 1        
        for network in networks:
            virshnet = VirshNetCommand(network, idx)
            virshnet.restart()
            idx += 1
            
        ansible_hosts = []
        for vm in vms:
            ansible_hosts.append(vm.get_name())    
        with open('ansible/ansible_hosts', 'w') as f:
            print >> f, '\n'.join(ansible_hosts)
            
    for vm in target_vms:
        if command == 'up':
            print bcolors.OKGREEN + 'start ' + vm.get_name() + bcolors.ENDC
            image = IMAGES_PATH + '/' + vm.get_name() + ".qcow2"
            if os.path.isfile(image):
                print "image file aleady exists : %s" % image
                virsh = VirshCommand(vm)
                virsh.start()
            else:
                qemu_img = QemuImgCommand(vm)
                qemu_img.create()
                virt_install = VirtInstallCommand(vm)
                virt_install.execute()
        if command == 'halt':
            print bcolors.OKGREEN + 'shutdown ' + vm.get_name() + bcolors.ENDC
            virsh = VirshCommand(vm)
            virsh.shutdown()
        if command == 'destroy':
            print bcolors.OKGREEN + 'destroy ' + vm.get_name() + bcolors.ENDC
            virsh = VirshCommand(vm)
            virsh.destroy()
            virsh.undefine()
            qemu_img = QemuImgCommand(vm)
            qemu_img.destroy()
            
    if command == 'status':
        print bcolors.OKGREEN + 'status\n' + bcolors.ENDC
        VirshStatusCommand().list()
            
    if command == 'up':
        print bcolors.OKGREEN + '\ninit VMs...' + bcolors.ENDC + '\n'
        
        os.chdir('./ansible')

        cmd = []
        cmd.append("ansible")
        cmd.append("all")
        cmd.append("-m")
        cmd.append("ping")

        print "wait for 10 seconds"
        time.sleep(10)
 
        for i in range(5):
            retcode = subprocess.call(cmd)
            if retcode == 0:
                print "run ansible-playbook"
                
                cmd = []
                cmd.append("ansible-playbook")
                cmd.append("-v")
                cmd.append("site.yml")
                subprocess.call(cmd)
                
                break
            
            print "wait for 5 seconds [%d]" % i 
            time.sleep(5)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit, sys_e:
        sys.exit(sys_e.code)