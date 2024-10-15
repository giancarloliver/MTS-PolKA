#!/usr/bin/python

from __future__ import print_function
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch
from mininet.term import makeTerm
import os
import sys
import subprocess
import time

# Configuration of switches and links
n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 10
BWE = 100

def create_network():
    os.system("sudo mn -c")
    net = Mininet_wifi()
    return net

def setup_topology(net):
    switches_n1 = []
    switches_n2 = []
    edges = []
    hosts = []

    try:
        # Adding hosts
        info("*** Adding hosts\n")
        for i in range(1, n_switches_E + 1):
            ip = f"10.0.{i}.{i}"
            mac = f"00:00:00:00:{i:02x}:{i:02x}"
            host = net.addHost(f"h{i}", ip=ip, mac=mac)
            hosts.append(host)

        # Adding level 1 core switches
        info("*** Adding P4Switches (core)\n")
        path = os.path.dirname(os.path.abspath(__file__))        
        for i in range(n_switches_C_N1):
            json_file = path + "/../m-polka/m-polka-core.json"
            config = path + f"/../m-polka/config/s1_{i}-commands.txt"

            switch = net.addSwitch(
                f"s1_{i}",
                netcfg=True,
                json=json_file,
                thriftport=50000 + i,
                switch_config=config,
                loglevel='error',
                cls=P4Switch,
            )
            switches_n1.append(switch)

        # Adding level 2 core switches
        for i in range(n_switches_C_N2):
            json_file = path + "/../m-polka/m-polka-core.json"
            config = path + f"/../m-polka/config/s2_{i}-commands.txt"

            switch = net.addSwitch(
                f"s2_{i}",
                netcfg=True,            
                json=json_file,
                thriftport=50002 + i,
                switch_config=config,
                loglevel='error',
                cls=P4Switch,
            )
            switches_n2.append(switch)

        # Adding edge switches
        info("*** Adding P4Switches (edge)\n")
        for i in range(1, n_switches_E + 1):
            json_file = path + "/../m-polka/m-polka-edge.json"
            config = path + f"/../m-polka/config/e{i}-commands.txt"

            edge = net.addSwitch(
                f"e{i}",
                netcfg=True,
                json=json_file,
                thriftport=50100 + i,
                switch_config=config,
                loglevel='info',
                cls=P4Switch,
            )
            edges.append(edge)

        # Creating links between devices
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

        # Starting the network
        info("*** Starting network\n")
        net.start()
        net.staticArp()
        net.waitConnected()

        mtu_value = 1400

        # Disabling offload for rx and tx on each host interface
        for host in hosts:
            host.cmd(f"ethtool --offload {host.name}-eth0 rx off tx off")
            host.cmd(f'ifconfig {host.defaultIntf()} mtu {mtu_value}')
            host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
            host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
            host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

        # # Setting MTU for h1-eth0 to 900 bytes
        h1 = net.get('h1')
        # h1.cmd("sudo ip link set dev h1-eth0 mtu 900")

        # Verifying MTU for h1-eth0
        mtu_output = h1.cmd("ip link show h1-eth0")
        info(f"MTU for h1-eth0: {mtu_output}")

        mtu_sw = 1500

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
    except Exception as e:
        info(f"Error setting up topology: {e}\n")
        net.stop()
        sys.exit(1)

    return net, hosts

def run_tests(net, hosts):
    h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')

    for test_number in range(1, 31):
        try:
            print(f"Running Test 4 - Iteration {test_number}")
            start_time = time.time()
            print(f"Starting Time: {start_time:.2f} seconds")

            print("Running Test 4 Perfil 0")

            print("Modifying E1")
            command = 'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:02:02 281023905350220 0" | simple_switch_CLI --thrift-port 50101'
            print(f"Executing: {command}")
            subprocess.run(command, shell=True)
            time.sleep(1)

            print("Modifying E2")
            command = 'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:01:01 109788155853315 0" | simple_switch_CLI --thrift-port 50102'
            print(f"Executing: {command}")
            subprocess.run(command, shell=True)
            time.sleep(1)

            print("Waiting for profile test")

            # Starting iperf server
            print(f"Start iperf server on h2 for test iteration {test_number}...")
            server_cmd = 'iperf3 -s &'
            print(f"Executing: {server_cmd}")
            h2.cmd(server_cmd)
            time.sleep(3)

            # Running iperf client
            iperf_cmd = f'iperf3 -c {h2.IP()} -n 10M --verbose &> data/run/output-P0-10M_{test_number}.txt'
            print(f"Executing: {iperf_cmd}")
            h1.cmd(iperf_cmd)

            # Stopping iperf
            os.system("killall iperf3")

            end_time = time.time()
            print(f"End Time: {end_time:.2f} seconds")
            total_execution_time = end_time - start_time
            print(f"Total Execution Time for iteration {test_number}: {total_execution_time:.2f} seconds")

        except Exception as e:
            print(f"Error during test iteration {test_number}: {e}")

if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")

    net = create_network()

    try:
        net, hosts = setup_topology(net)
        run_tests(net, hosts)
    finally:
        info("*** Stopping network\n")
        net.stop()
