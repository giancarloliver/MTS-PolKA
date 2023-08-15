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
import time

os.system("sudo mn -c")

n_switches_E = 2
n_switches_C = 7
BW = 10
NUM_TEST_ITERATIONS = 3

# Definicao nome arquivo bwm-ng
arq_bwm = "tmp.bwm"


TEST_FOLDER = "test"

def create_test_folder():
    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)

def monitor_bwm_ng(fname, interval_sec, test_num): 
    folder_path = os.path.join(TEST_FOLDER, f"test{test_num}")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    cmd = ("sleep 1; bwm-ng -t %s -o csv -u bytes -T rate -C ',' > %s.csv" % 
            (interval_sec * 1000, os.path.join(folder_path, fname)))
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

def run_iperf_test(h1, h2, profile, mac, field1, field2):
    iperf_cmd = f'iperf3 -u -c {h2.IP()} -t 35 -b 10M'
    h1.cmd(iperf_cmd + ' &')
    time.sleep(1)

    command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 {mac} {field1} {field2}" | simple_switch_CLI --thrift-port 50101'
    subprocess.run(command, shell=True)
    time.sleep(1)

    print(f"Aguardar para o teste do perfil {profile} durante 10 segundos")
    time.sleep(10)

def calculate_average_throughput(results):
    total_throughput = sum(results)
    num_results = len(results)
    if num_results == 0:
        return 0  # Return 0 if there are no results to avoid ZeroDivisionError
    average_throughput = total_throughput / num_results
    return average_throughput
 

if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    "Create a network."
    net = Mininet_wifi()

    topology(remote_controller) 

    create_test_folder()

    h1, h2 = net.get('h1', 'h2')

    h1.cmd('ifconfig h1-eth0 mtu 1400')
    h2.cmd('ifconfig h2-eth0 mtu 1400')

   #Start the network
   
    print ("Dumping host dumpNodeConnections")
    dumpNodeConnections(net.hosts)

    
    print("Start iperf server on h2...")
    h2.cmd('iperf3 -s &')
   

    # Definicao do monitor de vazao
    monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))

    # Chamada da funcao de monitoramento de pacotes de rede
    print("Start iperf server on bwm-ng...")
    monitor_cpu.start()
    time.sleep(1)
   

    iperf_cmd = f'iperf3 -u -c {h2.IP()} -t 35 -b 10M'
    h1.cmd(iperf_cmd + ' &')
    time.sleep(1)

    

    # Store the throughput results for each iteration
    throughput_results = []
    
    # Define the profiles to test
    profiles = [
        (11, "00:00:00:00:02:02", "73817044396459291349659850249", "37823969743312635090392551816"),
        (4, "00:00:00:00:02:02", "201075362587017487558704", "79664158660626060758226"),
        (0, "00:00:00:00:02:02", "37968085910475", "0")
    ]


    # Loop through each profile, execute the iperf3 test for the specified number of iterations
    for iteration in range(NUM_TEST_ITERATIONS):
        print(f"Running Test Iteration {iteration + 1}/{NUM_TEST_ITERATIONS}")
        start_time = time.time()
        print(f"Starting test: {start_time}")

        for profile, mac, field1, field2 in profiles:
            run_iperf_test(h1, h2, profile, mac, field1, field2)
            os.system("killall -9 iperf")

            # Save the bwm-ng throughput value for this iteration and profile
            monitor_bwm_ng(f"test{iteration + 1}_profile{profile}", 1.0, iteration + 1)
            with open(os.path.join(TEST_FOLDER, f"test{iteration + 1}_profile{profile}/test{iteration + 1}_profile{profile}.csv"), "r") as f:
                lines = f.readlines()
                if len(lines) > 2:
                    throughput_line = lines[-2].strip()
                    throughput_value = float(throughput_line.split(",")[1])  # Assuming throughput is in bytes per second
                    throughput_results.append(throughput_value)
            


    # Stop iperf3 and bwm-ng processes after all test iterations are complete
    os.system("killall -9 iperf")
    os.system("killall bwm-ng")

    

    # Calculate the average throughput
    average_throughput = calculate_average_throughput(throughput_results)
    print(f"Average Throughput over {NUM_TEST_ITERATIONS} iterations: {average_throughput} bps")


       
   

    # Encerramento do iperf e o  bwn-ng
    print("Stop iperf e bwn-ng")
    os.system("killall -9 iperf")
    os.system("killall bwm-ng")

    info("*** Stopping network\n")
    net.stop()