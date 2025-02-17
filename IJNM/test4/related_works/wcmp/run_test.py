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

import csv
import matplotlib.pyplot as plt
import numpy as np
import threading
import os
import subprocess
import time
from multiprocessing import Process
import _thread

n_switches_E = 16
n_switches_C_N1 = 2
n_switches_C_N2 = 5

BW = 1 # bandwidth core
BWE = 10 # bandwidth edger
D = 1 # delay

def create_data_directories():
    # Define the directories to create
    directories = [
        "latency_test/result",
        "latency_test/data/run",
        "fct/data/run",
        "fct/result"
    ]
    
    for directory in directories:
        # Check if the directory exists
        if not os.path.exists(directory):
            # Create the directory
            os.makedirs(directory)
            print(f"Directory {directory} created.")
        else:
            print(f"Directory {directory} already exists.")

# Function to generate iperf flows with a fixed size, 
def generate_flows(net, src, dst, lambda_rate, duration, flow_size_kb):
    """
    Generate iperf TCP flows from a fixed source to a fixed destination based on a Poisson distribution
    for the initiation rate. Each flow uses a fixed size of 100KB.
    
    :param net: Mininet network object
    :param src: Source host for iperf flows
    :param dst: Destination host for iperf flows
    :param lambda_rate: Average rate (events per second) for the Poisson distribution
    :param duration: Duration to run the experiment
    :param flow_size_kb: Fixed size of each flow (in Kilobytes)
    """
    end_time = time.time() + duration
    port = 5001  # Starting port number
    
    while time.time() < end_time:
        # Generate time until the next event using Poisson distribution
        delay = np.random.poisson(1 / lambda_rate)
        time.sleep(delay)
        
        # Define the fixed flow size in bytes
        flow_size_bytes = flow_size_kb * 1024  # Convert size to bytes
        
        # Convert bytes to megabytes for iperf usage
        flow_size_mb = flow_size_bytes / (1024 * 1024)
        
        # Check if the port is available
        if port > 65535:
            print("Port number exceeded range.")
            break
        
        # Start iperf server on the destination host if not already running
        dst_port = port
        if not dst.cmd(f'netstat -an | grep {dst_port}'):
            dst.cmd(f'iperf3 -s -p {dst_port} &')
        
        # Start iperf client on the source host        
        src.cmd(f'iperf3 -c {dst.IP()} -p {dst_port} -n {flow_size_mb:.2f}M &')
        
        # Increment the port number for the next flow
        port += 1


def monitor_bwm_ng(fname, interval_sec):
    cmd = f"sleep 1; bwm-ng -t {interval_sec * 1000} -o csv -u bytes -T rate -C ',' > {fname}"
    subprocess.Popen(cmd, shell=True).wait()


def topology(remote_controller):

    os.system("sudo mn -c")

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
        json_file = f"{path}/p4src/wcmp.json"
        config = f"{path}/lat-sw-commands/s1_{i}-commands.txt"

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
        json_file = f"{path}/p4src/wcmp.json"
        config = f"{path}/lat-sw-commands/s2_{i}-commands.txt"
       
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
        json_file = f"{path}/p4src/wcmp.json"
        config = f"{path}/lat-sw-commands/e{i}-commands.txt"
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
    for i in range(n_switches_E):
        net.addLink(hosts[i], edges[i], bw=BWE, delay=D)

    net.addLink(switches_n1[0], edges[0], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[1], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[2], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[3], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[4], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[5], bw=BWE, delay=D)  
    net.addLink(switches_n1[0], edges[6], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[7], bw=BWE, delay=D)  
    net.addLink(switches_n1[1], edges[8], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[9], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[10], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[11], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[12], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[13], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[14], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[15], bw=BWE, delay=D)
           
    for i in range(n_switches_C_N1):
        for j in range(n_switches_C_N2):
            net.addLink(switches_n1[i], switches_n2[j], bw=BW, delay=D)

            
    # "Integrando CLI mininet"
    info("*** Starting network\n")
    net.start()
    net.staticArp()
    net.waitConnected()

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

if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    # Create necessary data directories
    create_data_directories()

    "Create a network."
    net = Mininet_wifi()
    print('******************************************************')
    os.system("pwd")
    topology(remote_controller) 

    h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16 = net.get('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'h11', 'h12', 'h13', 'h14', 'h15', 'h16')    

    samples = 1
    test = 1

    for _ in range(samples):
        print(f"Running Test {test}")
        start_time = time.time()
        print(f"Starting Time: {start_time:.2f} seconds")

        arq_bwm = f"fct/data/run/{test}-tmp.bwm"
        monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))

        print("Start iperf server")
        h9.cmd('iperf3 -s &')        
        h11.cmd('iperf3 -s &')
        time.sleep(2)

        print("Starting bwm-ng")
        monitor_cpu.start()
        time.sleep(1)
               
        h1.cmd(f'iperf3 -c {h9.IP()} -n 100M --verbose &> fct/data/run/{samples}-iperf_h1_h9.txt &')

        h3.cmd(f'iperf3 -c {h11.IP()} -n 100M --verbose &> fct/data/run/{samples}-iperf_h3_h11.txt &')
      
        # Define fixed source and destination hosts for smaller flows
        src = net.get('h2')  # Fixed source host
        dst = net.get('h10')  # Fixed destination host

        # Generate flows based on Poisson distribution for initiation rate
        lambda_rate = 4 # Average rate of flow initiation (flows per second)
        duration = 400  # Duration of the experiment (seconds)
        flow_size_kb = 10 # Fixed size of each flow (in Kilobytes)

        method = "ecmp"

        # Latency test
        h4.cmd(f'ping {h12.IP()} > latency_test/data/run/{method}_path1.log &')
        h5.cmd(f'ping {h13.IP()} > latency_test/data/run/{method}_path2.log &')
        h6.cmd(f'ping {h14.IP()} > latency_test/data/run/{method}_path3.log &')
        h7.cmd(f'ping {h15.IP()} > latency_test/data/run/{method}_path4.log &')
        h8.cmd(f'ping {h16.IP()} > latency_test/data/run/{method}_path5.log &')

        generate_flows(net, src, dst, lambda_rate, duration, flow_size_kb)             
             
        time.sleep(400)

        end_time = time.time()
        print(f"End Time: {end_time:.2f} seconds")
        total_execution_time = end_time - start_time
        print(f"Total Execution Time: {total_execution_time:.2f} seconds")

        print("Stop iperf3 and bwm-ng")
        os.system("killall iperf3")
        os.system("killall bwm-ng")

        #os.system(f"cat fct/data/run6/{test}-tmp.bwm >> {bwm_file}")
        os.system(f"grep 's1_0-eth1' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth1-a{test}.csv")
        os.system(f"grep 's1_0-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth2-a{test}.csv") 
        os.system(f"grep 's1_0-eth3' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth3-a{test}.csv") 
        os.system(f"grep 's1_0-eth4' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth4-a{test}.csv") 
        os.system(f"grep 's1_0-eth5' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth5-a{test}.csv") 
        os.system(f"grep 's1_0-eth6' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth6-a{test}.csv") 
        os.system(f"grep 's1_0-eth7' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth7-a{test}.csv") 
        os.system(f"grep 's1_0-eth8' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_0-eth8-a{test}.csv")
        os.system(f"grep 's2_0-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s2_0-eth2-a{test}.csv") 
        os.system(f"grep 's2_1-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s2_1-eth2-a{test}.csv")
        os.system(f"grep 's2_2-eth3' fct/data/run/{test}-tmp.bwm > fct/data/run/s2_2-eth3-a{test}.csv")
        os.system(f"grep 's2_3-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s2_3-eth2-a{test}.csv")
        os.system(f"grep 's2_4-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s2_4-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth1' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_1-eth1-a{test}.csv")
        os.system(f"grep 's1_1-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_1-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth3' fct/data/run/{test}-tmp.bwm > fct/data/run/s1_1-eth3-a{test}.csv")    
        os.system(f"grep 'e1-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e1-eth2-a{test}.csv")      
        os.system(f"grep 'e2-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e2-eth2-a{test}.csv")   
        os.system(f"grep 'e3-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e3-eth2-a{test}.csv")   
        os.system(f"grep 'e4-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e4-eth2-a{test}.csv")   
        os.system(f"grep 'e5-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e5-eth2-a{test}.csv")  
        os.system(f"grep 'e6-eth2' fct/data/run/{test}-tmp.bwm > fct/data/run/e6-eth2-a{test}.csv")       
        time.sleep(1)          
        
        test += 1    
    
    info("*** Stopping network\n")
    net.stop()