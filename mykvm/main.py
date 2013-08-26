from mykvm import VERSION
from mykvm import BASE_IMAGES_PATH
from mykvm import IMAGES_PATH

from mykvm.model import NetDev
from mykvm.model import VM
from mykvm.model import Network

from mykvm.command import VirshNetCommand
from mykvm.command import VirshCommand
from mykvm.command import QemuImgCommand
from mykvm.command import VirtInstallCommand
from mykvm.command import VirshStatusCommand

from mykvm.util import bcolors

import sys
import os.path
import stat
import shutil
import yaml
import time
import subprocess
import pkg_resources

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
    print("mykvm " + VERSION)
    print("")
    print("Usage: mykvm command [<args>]")
    print("")
    print("Available subcommands:")
    print("    init")
    print("    up [<vm>]")
    print("    halt")
    print("    destroy")
    print("    status")
    print("")
    sys.exit(1)    

def main():
    if len(sys.argv) < 2:
        usage()

    command = sys.argv[1]
    if command not in ['init', 'up', 'halt', 'destroy', 'status']:
        usage()

    if command == 'init':
        print bcolors.OKGREEN + 'initialize mykvm' + bcolors.ENDC + '\n'

        install_data_dir = '/usr/local/share/mykvm'

        if not os.path.isfile('mykvm.yml'):
            print bcolors.OKGREEN + '* create mykvm.yml' + bcolors.ENDC
            src = install_data_dir + '/conf/mykvm.yml'
            shutil.copy(src, 'mykvm.yml')
            st = os.stat('mykvm.yml')
            os.chmod('mykvm.yml', st.st_mode | stat.S_IWRITE)

        if not os.path.exists('.mykvm/script'):
            print bcolors.OKGREEN + '* copy vmbuilder script' + bcolors.ENDC
            src = install_data_dir + '/script'
            shutil.copytree(src, '.mykvm/script')
            st = os.stat('.mykvm/script/vmbuilder.sh')
            os.chmod('.mykvm/script/vmbuilder.sh', st.st_mode | stat.S_IEXEC)

        if not os.path.exists('.mykvm/ansible'):
            print bcolors.OKGREEN + '* copy ansible files' + bcolors.ENDC
            src = install_data_dir + '/ansible'
            shutil.copytree(src, '.mykvm/ansible')

        base_image = BASE_IMAGES_PATH + '/' + "precise64.qcow2"
        if not os.path.isfile(base_image):
            print bcolors.OKGREEN + '* build base image ' + base_image + bcolors.ENDC
            cmd = []
            cmd.append(".mykvm/script/vmbuilder.sh")
            subprocess.call(cmd)
    
    if not os.path.exists(BASE_IMAGES_PATH):
        os.makedirs(BASE_IMAGES_PATH)
        
    if not os.path.exists(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)
    
    if not os.path.isfile('mykvm.yml'):
        print bcolors.OKGREEN + 'mykvm.yml does not exist' + bcolors.ENDC + '\n'
        sys.exit(1)

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
        for vm in target_vms:
            ansible_hosts.append(vm.get_name())    
        with open('.mykvm/ansible/ansible_hosts', 'w') as f:
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
        
        os.chdir('.mykvm/ansible')

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