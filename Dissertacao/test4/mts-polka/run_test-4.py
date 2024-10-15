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

n_switches_E = 6
n_switches_C_N1 = 2
n_switches_C_N2 = 5
n_hosts = 14

BW = 1 # bandwidth core
BWE = 10 # bandwidth edger
D = 1 # delay

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
        # print("TCP mouse flows from H2 to H5")
        src.cmd(f'iperf3 -c {dst.IP()} -p {dst_port} -n {flow_size_mb:.2f}M &')
        
        # Increment the port number for the next flow
        port += 1


def monitor_bwm_ng(fname, interval_sec):
    cmd = f"sleep 1; bwm-ng -t {interval_sec * 1000} -o csv -u bytes -T rate -C ',' > {fname}"
    subprocess.Popen(cmd, shell=True).wait()


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
    for i in range(1, n_hosts + 1):
        ip = "10.0.%d.%d" % (i, i)
        mac = "00:00:00:00:%02x:%02x" % (i, i)
        host = net.addHost("h%d" % i, ip=ip, mac=mac)
        hosts.append(host)

    info("*** Adding P4Switches (core)\n")
    for i in range(0, n_switches_C_N1):  # Add two level-1 switches
        path = os.path.dirname(os.path.abspath(__file__))        
        json_file = path + "/../../m-polka/m-polka-core.json"
        config =   path + "/../../m-polka/config/s1_{}-commands.txt".format(i)  # Update with the correct path

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
        json_file = path + "/../../m-polka/m-polka-core.json"
        config =   path + "/../../m-polka/config/s2_{}-commands.txt".format(i)  # Update with the correct path
       
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
        json_file = path + "/../../m-polka/m-polka-edge.json"
        config = path + "/../../m-polka/config/e{}-commands.txt".format(i)
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
    
    net.addLink(hosts[6], edges[0], bw=BWE, delay=D)
    net.addLink(hosts[7], edges[0], bw=BWE, delay=D)
    net.addLink(hosts[8], edges[0], bw=BWE, delay=D)
    net.addLink(hosts[9], edges[0], bw=BWE, delay=D)
    net.addLink(hosts[10], edges[3], bw=BWE, delay=D)
    net.addLink(hosts[11], edges[3], bw=BWE, delay=D)
    net.addLink(hosts[12], edges[3], bw=BWE, delay=D)
    net.addLink(hosts[13], edges[3], bw=BWE, delay=D)


    net.addLink(switches_n1[0], edges[0], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[1], bw=BWE, delay=D)
    net.addLink(switches_n1[0], edges[2], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[3], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[4], bw=BWE, delay=D)
    net.addLink(switches_n1[1], edges[5], bw=BWE, delay=D)  
        
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

    "Create a network."
    net = Mininet_wifi()
    print('******************************************************')
    os.system("pwd")
    topology(remote_controller) 

    h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14 = net.get('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'h11', 'h12', 'h13', 'h14')    


    samples = 1
    test = 1
    method = 'mts-polka'

    for _ in range(samples):
        print(f"Running Test {test}")
        start_time = time.time()
        print(f"Starting Time: {start_time:.2f} seconds")

        arq_bwm = f"fct_test/data/run/{test}-tmp.bwm"
        monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))

        print("Start iperf server")
        h5.cmd('iperf3 -s &')        
        h6.cmd('iperf3 -s &')
        # h15.cmd('iperf3 -s &')        
        # h16.cmd('iperf3 -s &')
        
        time.sleep(2)

        print("Starting bwm-ng")
        monitor_cpu.start()
        time.sleep(1)
               
        h2.cmd(f'iperf3 -c {h6.IP()} -n 100M --verbose &> fct_test/data/run/{samples}-iperf_h2_h6.txt &')
        h3.cmd(f'iperf3 -c {h5.IP()} -n 100M --verbose &> fct_test/data/run/{samples}-iperf_h3_h5.txt &')
        
        # h2.cmd(f'iperf3 -c {h16.IP()} -n 100M --verbose &> data/run/{samples}-iperf_h2_h16.txt &')
        # h3.cmd(f'iperf3 -c {h15.IP()} -n 100M --verbose &> data/run/{samples}-iperf_h3_h15.txt &')
        

        
        # Define fixed source and destination hosts for smaller flows
        src = net.get('h1')  # Fixed source host
        dst = net.get('h4')  # Fixed destination host

        # Generate flows based on Poisson distribution for initiation rate
        lambda_rate = 4 # Average rate of flow initiation (flows per second)
        duration = 400  # Duration of the experiment (seconds)
        flow_size_kb = 10 # Fixed size of each flow (in Kilobytes)

        #latency test

        h7.cmd(f'ping {h11.IP()} > latency_test/data/run/{method}_path1.log &')
        h8.cmd(f'ping {h12.IP()} > latency_test/data/run/{method}_path2.log &')
        h1.cmd(f'ping {h4.IP()} > latency_test/data/run/{method}_path3.log &')
        h9.cmd(f'ping {h13.IP()} > latency_test/data/run/{method}_path4.log &')
        h10.cmd(f'ping {h14.IP()} > latency_test/data/run/{method}_path5.log &')

        generate_flows(net, src, dst, lambda_rate, duration, flow_size_kb)
    
        time.sleep(400)

        end_time = time.time()
        print(f"End Time: {end_time:.2f} seconds")
        total_execution_time = end_time - start_time
        print(f"Total Execution Time: {total_execution_time:.2f} seconds")

        print("Stop iperf3 and bwm-ng")
        os.system("killall iperf3")
        os.system("killall bwm-ng")

        #os.system(f"cat data/run6/{test}-tmp.bwm >> {bwm_file}")
        os.system(f"grep 's1_0-eth1' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth1-a{test}.csv")
        os.system(f"grep 's1_0-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth2-a{test}.csv") 
        os.system(f"grep 's1_0-eth3' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth3-a{test}.csv") 
        os.system(f"grep 's1_0-eth4' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth4-a{test}.csv") 
        os.system(f"grep 's1_0-eth5' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth5-a{test}.csv") 
        os.system(f"grep 's1_0-eth6' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth6-a{test}.csv") 
        os.system(f"grep 's1_0-eth7' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth7-a{test}.csv") 
        os.system(f"grep 's1_0-eth8' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_0-eth8-a{test}.csv")
        os.system(f"grep 's2_0-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s2_0-eth2-a{test}.csv") 
        os.system(f"grep 's2_1-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s2_1-eth2-a{test}.csv")
        os.system(f"grep 's2_2-eth3' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s2_2-eth3-a{test}.csv")
        os.system(f"grep 's2_3-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s2_3-eth2-a{test}.csv")
        os.system(f"grep 's2_4-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s2_4-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth1' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_1-eth1-a{test}.csv")
        os.system(f"grep 's1_1-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_1-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth3' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/s1_1-eth3-a{test}.csv")    
        os.system(f"grep 'e1-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e1-eth2-a{test}.csv")      
        os.system(f"grep 'e2-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e2-eth2-a{test}.csv")   
        os.system(f"grep 'e3-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e3-eth2-a{test}.csv")   
        os.system(f"grep 'e4-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e4-eth2-a{test}.csv")   
        os.system(f"grep 'e5-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e5-eth2-a{test}.csv")  
        os.system(f"grep 'e6-eth2' fct_test/data/run/{test}-tmp.bwm > fct_test/data/run/e6-eth2-a{test}.csv")       
        time.sleep(1)          
        
        test += 1    
    
    info("*** Stopping network\n")
    net.stop()