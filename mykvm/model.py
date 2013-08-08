class VM(object):

    def __init__(self):
        self.name = ""
        self.vcpus = "1"
        self.kvm_nested = False
        self.ram = "1024"
        self.template = "precise64.qcow2"
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
        