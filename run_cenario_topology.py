#!/usr/bin/python
import os
import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.term import makeTerm
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink

from multiprocessing import Process
import os
from subprocess import Popen
from time import sleep
from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP

n_switches_E = 2
n_switches_C = 7
# BW = 10


def topology(remote_controller,net, hosts):
    # "Create a network."
    # net = Mininet_wifi()

    # linkopts = dict()
    switches = []
    edges = []
    #hosts = []

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
    
    for i in range(1, n_switches_C -1):
        net.addLink(switches[0], switches[i])

    for i in range(1, n_switches_C -1):
        net.addLink(switches[6], switches[i])
      
   
    
        
    
    

    # disabling offload for rx and tx on each host interface
    for host in hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))   
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")


   

    


if __name__ == "__main__":
    setLogLevel("info")
    remote_controller = False
    hosts = []
    net = Mininet_wifi()
    topology(remote_controller,net, hosts)

    #Definicao nome arquivo bwm-ng
    arq_bwm = "teste.bwm"

    #Definicao da funcao de monitoramento de pacotes de rede 
    def monitor_bwm_ng(fname, interval_sec): 
        cmd = ("sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' > %s" % 
                (interval_sec * 1000, fname)) 
        Popen(cmd, shell=True).wait()
        
    info("*** Starting network\n")
    net.start()
    net.staticArp()
    net.waitConnected()


    #definicao do monitor de vao
    monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))

    #Chamada da funcao de monitoramento de pacotes de rede
    monitor_cpu.start()

    #Inicia o teste de comunicacao de todos para todos 
   
       
    hosts[2].cmd('iperf3 -s -u -p 5001 > /dev/null &') 
    hosts[1].cmd('iperf3 -c 10.0.2.2 -u -k 10000  -p 5001  -i 1 -yc > /dev/null')          

    #Pausar o codigo para aguardar a finalização dos flux
    print('Aguarde ate que a experiencia seja concluida ...') 
    sleep(300)

    #Finalizar os processos de Iperf, bwm-ng
    os.system("killall -9 iperf") 
    os.system("killall -9 bwm-ng")

    #Finalizar o monitor de banda e a rede do Mininet
    monitor_cpu.terminate()
    print('Finalizado.')
    print('Arquivo BWM-NG gerado em: ',arq_bwm)
    

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()