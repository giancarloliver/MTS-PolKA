#!/usr/bin/python

from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, CPULimitedHost
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.util import irange, dumpNodeConnections

import os
import subprocess
import time
from multiprocessing import Process

n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 1
BWE = 10

pcap_dump = True


def topology(remote_controller):

    os.system("sudo mn -c")

    "Create a network."
    net = Mininet_wifi()

    switches_n1 = []
    switches_n2 = []
    edges = []
    hosts = []

    info("*** Adding hosts\n")
    for i in range(1, n_switches_E + 1):
        ip = f"10.0.{i}.{i}"
        mac = f"00:00:00:00:{i:02x}:{i:02x}"
        host = net.addHost(f"h{i}", ip=ip, mac=mac)
        hosts.append(host)

    path = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(path, "p4src/wcmp.json")

    info("*** Adding P4Switches (core)\n")
    for i in range(n_switches_C_N1):
        config = os.path.join(path, f"sw-commands/s1_{i}-commands.txt")
        switch = net.addSwitch(
            f"s1_{i}",
            netcfg=True,
            json=json_file,
            thriftport=50000 + i,
            pcap_dump="pcap_logs/",
            switch_config=config,
            loglevel='info',
            cls=P4Switch,
        )
        switches_n1.append(switch)

    for i in range(n_switches_C_N2):
        config = os.path.join(path, f"sw-commands/s2_{i}-commands.txt")
        switch = net.addSwitch(
            f"s2_{i}",
            netcfg=True,
            json=json_file,
            thriftport=50002 + i,
            pcap_dump="pcap_logs/",
            switch_config=config,
            loglevel='info',
            cls=P4Switch,
        )
        switches_n2.append(switch)

    info("*** Adding P4Switches (edge)\n")
    for i in range(1, n_switches_E + 1):
        config = os.path.join(path, f"sw-commands/e{i}-commands.txt")
        edge = net.addSwitch(
            f"e{i}",
            netcfg=True,
            json=json_file,
            thriftport=50100 + i,
            pcap_dump="pcap_logs/",
            switch_config=config,
            loglevel='info',
            cls=P4Switch,
        )
        edges.append(edge)

    info("*** Creating links\n")
    for i in range(n_switches_E):
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
    net.waitConnected()

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
    