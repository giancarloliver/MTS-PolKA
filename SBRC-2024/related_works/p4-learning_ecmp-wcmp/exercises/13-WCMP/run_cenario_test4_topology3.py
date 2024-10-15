#!/usr/bin/python

from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import P4Switch  # Importando o P4Switch

import os

n_switches_E = 2
n_switches_C_N1 = 2
n_switches_C_N2 = 3
BW = 10
BWE = 10

def topology(remote_controller):
    os.system("sudo mn -c")

    info("*** Creating network\n")
    net = Mininet(link=TCLink, switch=P4Switch)  # Usando P4Switch

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

    info("*** Adding core switches\n")
    for i in range(n_switches_C_N1):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-core.json"
        config = path + f"/m-polka/config/s1_{i}-commands.txt"
        switch = net.addSwitch(
            f"s1_{i}",
            json=json_file,
            thriftport=50000 + i,
            switch_config=config,
            loglevel='error',
            cls=P4Switch,  # Usando P4Switch
        )
        switches_n1.append(switch)

    for i in range(n_switches_C_N2):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-core.json"
        config = path + f"/m-polka/config/s2_{i}-commands.txt"
        switch = net.addSwitch(
            f"s2_{i}",
            json=json_file,
            thriftport=50002 + i,
            switch_config=config,
            loglevel='error',
            cls=P4Switch,  # Usando P4Switch
        )
        switches_n2.append(switch)

    info("*** Adding edge switches\n")
    for i in range(1, n_switches_E + 1):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + "/m-polka/m-polka-edge.json"
        config = path + f"/m-polka/config/e{i}-commands.txt"
        edge = net.addSwitch(
            f"e{i}",
            json=json_file,
            thriftport=50100 + i,
            switch_config=config,
            loglevel='info',
            cls=P4Switch,  # Usando P4Switch
        )
        edges.append(edge)

    info("*** Creating links\n")         
    for i in range(n_switches_E):
        net.addLink(hosts[i], edges[i], bw=BWE)

    net.addLink(switches_n1[0], edges[0], bw=BWE)
    net.addLink(switches_n1[1], edges[1], bw=BWE)

    for i in range(n_switches_C_N1):
        for j in range(n_switches_C_N2):
            net.addLink(switches_n1[i], switches_n2[j], bw=BW)

    info("*** Starting network\n")
    net.start()
    net.staticArp()

    mtu_value = 1400
    for host in hosts:
        host.cmd(f"ethtool --offload {host.name}-eth0 rx off tx off")
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
