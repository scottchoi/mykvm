#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import yaml
import os
import subprocess
import sys

BASE_IMAGES_PATH = os.getenv("HOME") + '/' + '.mykvm/base'
MYKVM_CONFIG_PATH = os.getcwd() + '/' + '.mykvm'
IMAGES_PATH = MYKVM_CONFIG_PATH + '/' + 'images'

class Network(object):

    def __init__(self):
        self.name = "default"
        self.ip  = ""
        self.mac = ""

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_ip(self):
        return self.ip

    def set_ip(self, ip):
        self.ip = ip
        self.mac = "52:54:00:00:00:" + self.ip.split('.')[-1]

    def get_mac(self):
        return self.mac

    def __str__(self):
        config = "network: "
        config += ("name=%s "  % self.name)
        config += ("mac=%s "   % self.mac)
        if self.ip:
            config += ("ip=%s" % self.ip)

        return config

class VM(object):

    def __init__(self, name):
        self.name = name
        self.vcpus = "1"
        self.ram = "1024"
        self.template = "precise-base.qcow2"
        self.networks = []

    def get_name(self):
        return self.name

    def set_vcpus(self, vcpus):
        self.vcpus = str(vcpus)

    def get_ram(self):
        return self.ram

    def set_ram(self, ram):
        self.ram = str(ram)

    def get_template(self):
        return self.template

    def set_template(self, template):
        self.template = template

    def get_networks(self):
        return self.networks

    def add_network(self, network):
        self.networks.append(network)

    def __str__(self):
        config = "vm: "
        config += ("name=%s "    % self.name)
        config += ("vcpus=%s "   % self.vcpus)
        config += ("ram=%s "     % self.ram)
        config += ("template=%s" % self.template)
        
        for network in self.networks:
            config += "\n\t" + network.__str__()

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
        cmd.append("--cpu")
        cmd.append("core2duo,+vmx") 
        cmd.append("--ram")
        cmd.append(self.vm.get_ram())
        cmd.append("--disk")
        cmd.append(IMAGES_PATH + '/' + self.vm.get_name() + ".qcow2,format=qcow2")
        for network in self.vm.get_networks():
            cmd.append("--network")
            cmd.append("network=" + network.get_name())
            if network.get_mac():
                cmd.append("--mac")
                cmd.append(network.get_mac()) 
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

class DnsmasqCommand(object):

    NET_CONFIG_FILE = MYKVM_CONFIG_PATH + '/' + 'default_net.xml'
    DEFAULT_NET_CONFIG = """
<network>
  <name>default</name>
  <uuid>14a108fe-9ae5-809a-aadb-12a828d1d602</uuid>
  <forward mode='nat'/>
  <bridge name='virbr0' stp='on' delay='0' />
  <mac address='52:54:00:4A:0F:F1'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254' />
{{ host_info }}      
    </dhcp>
  </ip>
</network>
    """

    def __init__(self, vms):
        self.vms = vms

    def generate_net_config(self):
        hosts = []
        for vm in self.vms:
            name = vm.get_name()
            network = vm.get_networks()[0]
            ip = network.get_ip()
            mac = network.get_mac()
            hosts.append("      <host mac='%s' name='%s' ip='%s' />" % (mac, name, ip))

        host_info = "\n".join(hosts)

        with open(self.NET_CONFIG_FILE, 'w') as f:
            print >> f, self.DEFAULT_NET_CONFIG.replace('{{ host_info }}', host_info)

    def restart(self):
        cmd = []

        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-destroy")
        cmd.append("default")

        subprocess.call(cmd)
        
        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-undefine")
        cmd.append("default")

        subprocess.call(cmd)

        self.generate_net_config()

        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-define")
        cmd.append("--file")
        cmd.append(self.NET_CONFIG_FILE)

        subprocess.call(cmd)

        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-start")
        cmd.append("default")

        subprocess.call(cmd)
        
        cmd = []
        cmd.append("sudo")
        cmd.append("virsh")
        cmd.append("net-autostart")
        cmd.append("default")

        subprocess.call(cmd)
        
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

def create_network(network_config):
    network = Network()
    
    name = network_config.get('name')
    ip = network_config.get('ip')
    mac = network_config.get('mac')
    
    if name:
        network.set_name(name)
    if ip:
        network.set_ip(ip)
    if mac:
        network.set_mac(mac)

    return network


def create_vm(vm_config):
    vm = VM(vm_config.get('name'))

    vcpus = vm_config.get('vcpus')
    ram = vm_config.get('ram')
    template = vm_config.get('template')

    if vcpus:
        vm.set_vcpus(vcpus)
    if ram:
        vm.set_ram(ram)
    if template:
        vm.set_template(template)
    
    networks_config = vm_config.get('networks')
    for network_config in networks_config:		
        vm.add_network(create_network(network_config))

    return vm

def usage():
    print("Usage: mykvm command [<vm name>]")
    print("")
    print("Available subcommands:")
    print("    start")
    print("    stop")
    print("    status")
    print("")
    sys.exit(1)    

def main():
    if len(sys.argv) < 2:
        usage()

    command = sys.argv[1]
    if command not in ['start', 'stop', 'status']:
        usage()
    
    if not os.path.exists(BASE_IMAGES_PATH):
        os.makedirs(BASE_IMAGES_PATH)
        
    if not os.path.exists(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)
    
    vms = []
    with open('mykvm.yml', 'r') as f:
        vms_config = yaml.load(f)
    
        for vm_config in vms_config:
            vms.append(create_vm(vm_config))
    
    target_vms = []
    if len(sys.argv) > 2:
        vm_name = sys.argv[2]
        for vm in vms:
            if vm_name == vm.get_name():
                target_vms.append(vm)
                break
    else:
        target_vms = vms
    
    if command == 'start':
        print bcolors.OKGREEN + 'restart dnsmasq' + bcolors.ENDC
        dnsmasq = DnsmasqCommand(vms)
        dnsmasq.restart()
    
    if command == 'status':
        print bcolors.OKGREEN + 'status\n' + bcolors.ENDC
        VirshStatusCommand().list()
    
    for vm in target_vms:
        if command == 'start':
            print bcolors.OKGREEN + 'start ' + vm.get_name() + bcolors.ENDC
            qemu_img = QemuImgCommand(vm)
            qemu_img.create()
            virt_install = VirtInstallCommand(vm)
            virt_install.execute()
        if command == 'stop':
            print bcolors.OKGREEN + 'stop ' + vm.get_name() + bcolors.ENDC
            virsh = VirshCommand(vm)
            virsh.destroy()
            virsh.undefine()
            qemu_img = QemuImgCommand(vm)
            qemu_img.destroy()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit, sys_e:
        sys.exit(sys_e.code)