#!/usr/bin/python

from __future__ import print_function
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from multiprocessing import Process
from subprocess import Popen
from time import sleep

from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.term import makeTerm
from mininet.node import CPULimitedHost

import os
import sys
import subprocess
import time

# Configuração dos switches e links
n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 10
BWE = 100


def topology(remote_controller):
    os.system("sudo mn -c")

    # Inicialização das listas de switches e hosts
    switches_n1 = []
    switches_n2 = []
    edges = []
    hosts = []

    # Adicionando hosts
    info("*** Adding hosts\n")
    for i in range(1, n_switches_E + 1):
        ip = "10.0.%d.%d" % (i, i)
        mac = "00:00:00:00:%02x:%02x" % (i, i)
        host = net.addHost("h%d" % i, ip=ip, mac=mac)
        hosts.append(host)

    # Adicionando switches de nível 1 (core)
    info("*** Adding P4Switches (core)\n")
    for i in range(n_switches_C_N1):
        path = os.path.dirname(os.path.abspath(__file__))        
        json_file = path + "/../m-polka/m-polka-core.json"
        config = path + "/../m-polka/config/s1_{}-commands.txt".format(i)

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

    # Adicionando switches de nível 2 (core)
    for i in range(n_switches_C_N2):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/../m-polka/m-polka-core.json"
        config = path + "/../m-polka/config/s2_{}-commands.txt".format(i)
       
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

    # Adicionando switches de borda
    info("*** Adding P4Switches (edge)\n")
    for i in range(1, n_switches_E + 1):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/../m-polka/m-polka-edge.json"
        config = path + "/../m-polka/config/e{}-commands.txt".format(i)
        
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

     # Criando links entre os dispositivos
    info("*** Creating links\n")
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
            
    # Iniciando a rede
    info("*** Starting network\n")
    net.start()
    net.staticArp()
    net.waitConnected()

    mtu_value = 900

    # Desabilitando offload para rx e tx em cada interface de host
    for host in hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        host.cmd(f'ifconfig {host.defaultIntf()} mtu {mtu_value}')
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    mtu_sw = 1400

    # Setting MTU for all switches' interfaces to 1500 bytes
    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        for intf in sw.intfList():
            if intf.name != 'lo':
                sw.cmd(f"sudo ip link set dev {intf.name} mtu {mtu_sw}")

    # Verifying MTU for switches' interfaces
        for sw in net.switches:
            for intf in sw.intfList():
                if intf.name != 'lo':
                    mtu_output = sw.cmd(f"ip link show {intf.name}")
                    info(f"MTU for {intf.name} on {sw.name}: {mtu_output}")               


if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    # Criação da rede
    net = Mininet_wifi()

    try:
        topology(remote_controller) 

        h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')  

        for test_number in range(1, 5):
            print(f"Running Test 4 - Iteration {test_number}")
            start_time = time.time()
            print(f"Starting Time: {start_time:.2f} seconds")

            print("Running Test 4 Perfil 0")

            print("Alterando E1")
            command = 'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:02:02 281023905350220 0" | simple_switch_CLI --thrift-port 50101'
            print(f"Executing: {command}")
            subprocess.run(command, shell=True)
            time.sleep(1)

            print("Alterando E2")
            command = 'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:01:01 109788155853315 0" | simple_switch_CLI --thrift-port 50102'
            print(f"Executing: {command}")
            subprocess.run(command, shell=True)
            time.sleep(1)

            print("Aguardando para o teste do perfil")

            # Iniciando o monitoramento e servidor iperf
            print(f"Start iperf server on h2 for test iteration {test_number}...")
            server_cmd = f'iperf3 -s &'
            print(f"Executing: {server_cmd}")
            h2.cmd(server_cmd)
            time.sleep(3)

            # Set TCP window size (adjust as needed)e
            # tcp_window_size = "1M" 
            
            # Iniciando o iperf cliente
            iperf_cmd = f'iperf3 -c {h2.IP()} -n 10M --verbose &> data/run/output-P0-10M_{test_number}.txt'
            print(f"Executing: {iperf_cmd}")
            h1.cmd(iperf_cmd)
            # time.sleep(15)  # Adicione tempo de espera para garantir que o iperf3 conclua

            # Parando iperf
            os.system("killall iperf3")
                
            end_time = time.time()
            print(f"End Time: {end_time:.2f} seconds")
            total_execution_time = end_time - start_time
            print(f"Total Execution Time for iteration {test_number}: {total_execution_time:.2f} seconds")

    finally:
        info("*** Stopping network\n")
        net.stop()
