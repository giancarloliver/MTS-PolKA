#!/usr/bin/python

from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.node import CPULimitedHost
from mininet.util import irange, dumpNodeConnections

import os
import subprocess
import time
from multiprocessing import Process

n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 10
BWE = 100


    
def topology(remote_controller):

    os.system("sudo mn -c")

    "Create a network."
    net = Mininet_wifi()

    # linkopts = dict()
    switches_n1 = []
    switches_n2 = []
    edges = []
    hosts = []

    info("*** Adding hosts\n")
    for i in range(1, n_switches_E + 1):
        ip = "10.0.%d.%d" % (i, i)
        mac = "00:00:00:00:%02x:%02x" % (i, i)
        host = net.addHost("h%d" % i, ip=ip, mac=mac)
        hosts.append(host)

    info("*** Adding P4Switches (core)\n")
    for i in range(0, n_switches_C_N1):  # Add two level-1 switches
        path = os.path.dirname(os.path.abspath(__file__))        
        json_file = path + "/m-polka/m-polka-core.json"
        config =   path + "/m-polka/config/s1_{}-commands.txt".format(i)  # Update with the correct path

        switch = net.addSwitch(
            "s1_{}".format(i),
            netcfg=True,
            json=json_file,
            thriftport=50000 + i,
            switch_config=config,
            loglevel='error',
            cls=P4Switch,
        )
        switches_n1.append(switch)

    for i in range(0, n_switches_C_N2):  # Add five level-2 switches      
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-core.json"
        config =   path + "/m-polka/config/s2_{}-commands.txt".format(i)  # Update with the correct path
       
        switch = net.addSwitch(
           "s2_{}".format(i),
            netcfg=True,            
            json=json_file,
            thriftport=50002 + i,
            switch_config=config,
            loglevel='error',
            cls=P4Switch,
        )
        switches_n2.append(switch)



    info("*** Adding P4Switches (edge)\n")
    for i in range(1, n_switches_E + 1):
        # read the network configuration
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-edge.json"
        config = path + "/m-polka/config/e{}-commands.txt".format(i)
        # add P4 switches (core)
        edge = net.addSwitch(
            "e{}".format(i),
            netcfg=True,
            json=json_file,
            thriftport=50100 + int(i),
            switch_config=config,
            loglevel='info',
            cls=P4Switch,
        )
        edges.append(edge)

    info("*** Creating links\n")         

    # Links between hosts and edge switches
    for i in range(0, n_switches_E):
        net.addLink(hosts[i], edges[i], bw=BWE)

    net.addLink(switches_n1[0], edges[0], bw=BWE)
    net.addLink(switches_n1[1], edges[1], bw=BWE)    
    net.addLink(switches_n1[1], edges[3], bw=BWE)
    net.addLink(switches_n1[1], edges[4], bw=BWE) 

    net.addLink(switches_n2[2], edges[2], bw=BWE) 

    for i in range(n_switches_C_N1):
        for j in range(n_switches_C_N2):
            net.addLink(switches_n1[i], switches_n2[j], bw=BW)
            
    info("*** Starting network\n")
    net.start()
    net.staticArp()


    mtu_value = 1400

    # Disabling offload for rx and tx on each host interface
    for host in hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        host.cmd(f'ifconfig {host.defaultIntf()} mtu {mtu_value}')
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    info("*** Running CLI\n")
    CLI(net)

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    remote_controller = False
    topology(remote_controller)