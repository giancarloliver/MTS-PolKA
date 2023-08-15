#!/usr/bin/python

from __future__ import print_function
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel

from mininet.log import setLogLevel, info
from mininet.node import RemoteController

from multiprocessing import Process
from subprocess import Popen
from time import sleep

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.term import makeTerm
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections

import os
import sys
import pdb
import subprocess



n_switches_E = 2
n_switches_C = 7
BW = 10

# Definicao nome arquivo bwm-ng
arq_bwm = "tmp.bwm"

def topology(remote_controller):
    
    # linkopts = dict()
    switches = []
    edges = []
    hosts = []

    info("*** Adding hosts\n")
    for i in range(1, n_switches_E + 1):
        ip = "10.0.%d.%d" % (i, i)
        mac = "00:00:00:00:%02x:%02x" % (i, i)
        host = net.addHost("h%d" % i, ip=ip, mac=mac)
        hosts.append(host)

    info("*** Adding P4Switches (core)\n")
    for i in range(1, n_switches_C + 1):
        # read the network configuration
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-core.json"
        config = path + "/m-polka/config/s{}-commands.txt".format(i)
        # Add P4 switches (core)
        switch = net.addSwitch(
            "s{}".format(i),
            netcfg=True,
            json=json_file,
            thriftport=50000 + int(i),
            switch_config=config,
            loglevel='debug',
            cls=P4Switch,
        )
        switches.append(switch)

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
            loglevel='debug',
            cls=P4Switch,
        )
        edges.append(edge)

    info("*** Creating links\n")
    for i in range(0, n_switches_E):
        net.addLink(hosts[i], edges[i])
    net.addLink(switches[0], edges[0])
    net.addLink(switches[6], edges[1])
    
    for i in range(1, n_switches_C - 1):
        net.addLink(switches[0], switches[i])

    for i in range(1, n_switches_C - 1):
        net.addLink(switches[6], switches[i])

    # "Integrando CLI mininet"
    info("*** Starting network\n")
    net.start()
    net.staticArp()
    net.waitConnected()

    # Disabling offload for rx and tx on each host interface
    for host in hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    # # Definicao do monitor de vao
    # monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))

    # # Chamada da funcao de monitoramento de pacotes de rede
    # monitor_cpu.start()



# #Definicao da funcao de monitoramento de pacotes de rede 
# def monitor_bwm_ng(fname, interval_sec): 
#     cmd = ("sleep 1; bwm-ng -t %s -o csv -u bytes -T rate -C ',' > %s" % 
#             (interval_sec * 1000, fname)) 
#     Popen(cmd, shell=True).wait()


if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    "Create a network."
    net = Mininet_wifi()

    topology(remote_controller) 

    h1, h2 = net.get('h1', 'h2')

   #Start the network
   
    print ("Dumping host dumpNodeConnections")
    dumpNodeConnections(net.hosts)

    
    print("Start iperf server on h2...")
    h2.cmd("iperf3 -s &")

    

    # print("Start bwm-ng on h1 and h2...")
    # h1.sendcmd = ("bwm-ng -t 10 -o csv -u bytes-T rate -C ',' > h1.csv")
    # h2.sendcmd = ("bwm-ng -t 10 -o csv -u bytes-T rate -C ',' > h2.csv")

   

    # Start the iperf client on h1
    print("Start iperf client on h1...")

    h1.cmd('iperf3 -u -c ', h2.IP() + ' -t 40  -b 10M >  client_output.csv')
    # h1.cmd('iperf -M 1200 -c ', h2.IP() + ' -t 120 >  client_output.csv &')
    #net.iperf((h1, h2))
    os.system("./gen_test2.sh")
    


    
    # Stop the iperf server on h2 if it's running
    if h2.cmd("pgrep -x iperf"):
        print("Stopping iperf server on h2...")
        h2.cmd("killall -9 iperf")

    # Print link information for debugging
    print("Dumping link info...")
    dumpNodeConnections(net.switches)

    info("*** Stopping network\n")
    net.stop()