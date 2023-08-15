#!/usr/bin/python

from __future__ import print_function
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel

from mininet.log import setLogLevel, info
from mininet.node import RemoteController

from multiprocessing import Process
from subprocess import Popen, PIPE
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
import time

os.system("sudo mn -c")

n_switches_E = 2
n_switches_C = 7
BW = 100


def monitor_bwm_ng(fname, interval_sec): 
    cmd = ("sleep 1; bwm-ng -t %s -o csv -u bytes -T rate -C ',' > %s" % 
            (interval_sec * 1000, fname)) 
    Popen(cmd, shell=True).wait()

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
            loglevel='error',
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
            loglevel='error',
            cls=P4Switch,
        )
        edges.append(edge)

    info("*** Creating links\n")
    for i in range(0, n_switches_E):
        net.addLink(hosts[i], edges[i], bw=BW)
    net.addLink(switches[0], edges[0], bw=BW)
    net.addLink(switches[6], edges[1], bw=BW)
    
    for i in range(1, n_switches_C - 1):
        net.addLink(switches[0], switches[i], bw=BW)

    for i in range(1, n_switches_C - 1):
        net.addLink(switches[6], switches[i], bw=BW)

    # "Integrando CLI mininet"
    info("*** Starting network\n")
    net.start()
    net.staticArp()
    net.waitConnected()

    # Disabling offload for rx and tx on each host interface
    mtu_value = 1400
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

if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    "Create a network."
    net = Mininet_wifi()

    topology(remote_controller) 

    h1, h2 = net.get('h1', 'h2')

    print(f"Running Test")   
    start_time = time.time()
    print(f"Starting Time: {start_time:.2f} seconds")  

    # Chamada da funcao de monitoramento de pacotes de rede
    print("Start iperf server on bwm-ng...")
    # Start the iperf server on h2
    h2.cmd('iperf3 -s &')
    time.sleep(1)

    # # Definicao nome arquivo bwm-ng
    arq_bwm = 'run/data/w0.bwm'

    # # Definicao do monitor de vazao
    monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))  
    monitor_cpu.start()
    time.sleep(1)    
 
    # Modificar a tabela P4 com as informações do perfil
    command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 37968085910475 0" | simple_switch_CLI --thrift-port 50101'
    subprocess.run(command, shell=True)
    time.sleep(1)

    # Aguardar um tempo para que a tabela seja atualizada antes de executar o teste
    print(f"Aguardar para o teste do perfil 0 enviando 100000 pacotes udp")          
    # Start the iperf client on h1
    iperf_cmd = f'iperf3 -c {h2.IP()}  -u -k 100000'
    h1.cmd(iperf_cmd + ' &')
    time.sleep(1)
    
    # Stop iperf and bwm-ng
    print("Stop iperf e bwm-ng")
    os.system("killall iperf3")      

    end_time = time.time()
    print(f"End Time: {end_time:.2f} seconds")
    total_execution_time = end_time - start_time
    print(f"Total Execution Time: {total_execution_time:.2f} seconds")    

    info("*** Stopping network\n")
    net.stop()