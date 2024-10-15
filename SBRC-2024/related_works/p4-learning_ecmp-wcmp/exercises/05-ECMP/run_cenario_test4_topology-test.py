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
import time
import threading
import subprocess
import os
import subprocess
import time
from multiprocessing import Process
import _thread

# Número de switches e largura de banda
n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 10
BWE = 100


# Function to generate iperf3 flows with a fixed size


def generate_flows(net, src, dst, lambda_rate, duration, flow_size_kb):
    """
    Generate iperf3 TCP flows from a fixed source to a fixed destination based on a Poisson distribution
    for the initiation rate. Each flow uses a fixed size defined by flow_size_kb.
    
    :param net: Mininet network object
    :param h2: Source host for iperf3 flows
    :param h5: Destination host for iperf3 flows
    :param lambda_rate: Average rate (events per second) for the Poisson distribution
    :param duration: Duration to run the experiment
    :param flow_size_kb: Fixed size of each flow (in Kilobytes)
    """
    end_time = time.time() + duration
    port = 5001  # Starting port number    
    

    while time.time() < end_time:
        # Generate time until the next event using Exponential distribution
        delay = np.random.exponential(1 / lambda_rate)
        time.sleep(delay)
        
        # Define the fixed flow size in bytes
        flow_size_bytes = flow_size_kb * 1024  # Convert size to bytes
        
        # Convert bytes to megabytes for iperf3 usage
        flow_size_mb = flow_size_bytes / (1024 * 1024)

        # Check if the port is available
        if port > 65535:
            print("Port number exceeded range.")
            break        

        # Start iperf server on the destination host if not already running
        dst_port = port

        print(dst)
    

        if not dst.cmd(f'netstat -an | grep {dst_port}'):
            dst.cmd(f'iperf3 -s -p {dst_port} &') 
            time.sleep(2)  

        print(f'iperf3 -s -p {dst_port} &') 

        
        
        # # # Start iperf3 client on the source host
        src.cmd(f'iperf3 -c {dst.IP()} -p {port} -n {flow_size_mb:.2f}M &')

        print(f'iperf3 -c {dst.IP()} -p {port} -n {flow_size_mb:.2f}M &')        
        
        # Increment the port number for the next flow
        port += 1


# Function to start elephant flows at specific times
def start_elephant_flows(net, h1, h4, flow_size_mb, start_times):
    """
    Inicia fluxos TCP grandes entre src e dst nos tempos de início especificados.

    :param net: Objeto de rede Mininet
    :param h1: Host de origem para os fluxos TCP grandes
    :param h4: Host de destino para os fluxos TCP grandes
    :param flow_size_mb: Tamanho de cada fluxo elefante (em Megabytes)
    :param start_times: Lista de tempos (em segundos) para iniciar cada fluxo elefante
    """
    start_time_0 = time.time()  # Tempo de referência inicial
    for offset in start_times:
        # Calcula o tempo exato de início relativo ao tempo inicial
        time_to_wait = max(0, start_time_0 + offset - time.time())
        time.sleep(time_to_wait)
        print(f"Starting large TCP flow between {h1.name} and {h4.name} of size {flow_size_mb}MB")
        h4.cmd(f'iperf3 -s -p 5002 &')
        time.sleep(1)  # Espera para garantir que o servidor esteja em execução
        h1.cmd(f'iperf3 -c {h4.IP()} -p 5002 -n {flow_size_mb}M &')


# Function to monitor latency and save to CSV
def monitor_latency(src, dst, interval_ms, csv_file):
    """
    Monitor latency between src and dst using ping and save results to a CSV file.
    
    :param src: Source host for ping
    :param dst: Destination host for ping
    :param interval_ms: Interval (in milliseconds) between ping tests
    :param csv_file: Path to the CSV file to save latency information
    """
    interval_s = interval_ms / 1000.0  # Convert milliseconds to seconds
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Source', 'Destination', 'Latency (ms)'])
        
        while True:
            # Run ping command
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            output = src.cmd(f'ping -c 1 {dst.IP()}')
            latency = None
            for line in output.split('\n'):
                if 'time=' in line:
                    latency = line.split('time=')[1].split(' ')[0]
                    break
            
            # Write latency information to CSV
            writer.writerow([timestamp, src.name, dst.name, latency])
            print(f"Logged latency from {src.name} to {dst.name}: {latency}")
            
            # Wait before the next ping
            time.sleep(interval_s)

# Function to monitor throughput with bwm-ng and save to CSV
def monitor_throughput(host, csv_file, interval_s):
    """
    Monitor throughput on the given host using bwm-ng and save results to a CSV file.
    
    :param host: Host to monitor
    :param csv_file: Path to the CSV file to save throughput information
    :param interval_s: Interval (in seconds) between measurements
    """
    # Start bwm-ng command and capture its output
    command = f'bwm-ng -T -c 1 -o csv -u Mbit -i {int(interval_s * 1000)}'
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Interface', 'Rx (Mbit/s)', 'Tx (Mbit/s)'])
        
        while True:
            try:
                process = host.popen(command)
                output = process.communicate(timeout=interval_s)[0].decode()
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Process output to extract throughput values
                lines = output.splitlines()
                for line in lines:
                    if 'interface' in line:
                        parts = line.split(';')
                        interface = parts[0]
                        rx = parts[1]
                        tx = parts[2]
                        writer.writerow([timestamp, interface, rx, tx])
                        print(f"Logged throughput for {host.name}: Interface {interface}, Rx {rx}, Tx {tx}")
            
            except subprocess.TimeoutExpired:
                print(f"bwm-ng command timed out on {host.name}")
            
            # Wait before the next measurement
            time.sleep(interval_s)

# Function to plot latency from CSV file
def plot_latency(csv_file):
    """
    Plot latency data from a CSV file.
    
    :param csv_file: Path to the CSV file with latency data
    """
    timestamps = []
    latencies = []
    
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamps.append(row['Timestamp'])
            latencies.append(float(row['Latency (ms)']) if row['Latency (ms)'] else None)
    
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, latencies, marker='o', linestyle='-', color='b')
    plt.xlabel('Timestamp')
    plt.ylabel('Latency (ms)')
    plt.title('Latency Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig('latency_plot.png')
    plt.show()

# Function to plot throughput from CSV file
def plot_throughput(csv_file):
    """
    Plot throughput data from a CSV file.
    
    :param csv_file: Path to the CSV file with throughput data
    """
    timestamps = []
    rx_values = []
    tx_values = []
    
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamps.append(row['Timestamp'])
            rx_values.append(float(row['Rx (Mbit/s)']) if row['Rx (Mbit/s)'] else None)
            tx_values.append(float(row['Tx (Mbit/s)']) if row['Tx (Mbit/s)'] else None)
    
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, rx_values, marker='o', linestyle='-', color='r', label='Rx (Mbit/s)')
    plt.plot(timestamps, tx_values, marker='o', linestyle='-', color='g', label='Tx (Mbit/s)')
    plt.xlabel('Timestamp')
    plt.ylabel('Throughput (Mbit/s)')
    plt.title('Throughput Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.legend()
    plt.savefig('throughput_plot.png')
    plt.show()

    
def topology(remote_controller):

    os.system("sudo mn -c")    

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
    for i in range(n_switches_C_N1):  # Add two level-1 switches
        path = os.path.dirname(os.path.abspath(__file__))        
        json_file = f"{path}/p4src/ecmp.json"
        config = f"{path}/sw-commands/s1_{i}-commands.txt"

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

    for i in range(n_switches_C_N2):  # Add five level-2 switches      
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = f"{path}/p4src/ecmp.json"
        config = f"{path}/sw-commands/s2_{i}-commands.txt"
       
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

    info("*** Adding P4Switches (edge)\n")
    for i in range(1, n_switches_E + 1):
        path = os.path.dirname(os.path.abspath(__file__))
        json_file = f"{path}/p4src/ecmp.json"
        config = f"{path}/sw-commands/e{i}-commands.txt"
        
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

    info("*** Creating links\n")
    for i in range(n_switches_E):
        net.addLink(hosts[i], edges[i], bw=BWE)

    net.addLink(switches_n1[0], edges[0], bw=BWE)
    net.addLink(switches_n1[0], edges[1], bw=BWE)
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

    mtu_value = 1400

    # Desabilitando offload e configurando MTU
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

    ###################teste################################
   

    
if __name__ == "__main__":
    os.system("sudo mn -c")
    setLogLevel("info")
    remote_controller = False

    "Create a network."
    net = Mininet_wifi()
    print('******************************************************')
    os.system("pwd")
    topology(remote_controller) 

    h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5') 
    
    # Define fixed source and destination hosts for smaller flows
    src = net.get('h2')  # Fixed source host
    dst = net.get('h5')  # Fixed destination host

    # Generate flows based on Poisson distribution for initiation rate
    lambda_rate = 10   # Average rate of flow initiation (flows per second)
    duration = 60      # Duration of the experiment (seconds)
    flow_size_kb = 100 # Fixed size of each flow (in Kilobytes)

    # generate_flows(net, src, dst, lambda_rate, duration, flow_size_kb)

    # threading.Thread(target=generate_flows, args=(net, src, dst, lambda_rate, duration, flow_size_kb)).start()

    # Executar funções em processos separados para rodar em paralelo
    flow_process = Process(target=generate_flows, args=(net, src, dst, lambda_rate, duration, flow_size_kb))
  

    # Start large TCP elephant flows from h5 to h4 at specific times
    h1 = net.get('h1')
    h4 = net.get('h4')
    flow_size_mb = 100  # Size of each elephant flow (in Megabytes)
    start_times = [5, 10, 15]     # Start times for the elephant flows   


    # threading.Thread(target=start_elephant_flows, args=(net, h1, h4, elephant_flow_size_mb, start_times)).start()

    elephant_process = Process(target=start_elephant_flows, args=(net, h1, h4, flow_size_mb, start_times))

    
    # Monitor latency between each pair of hosts
    interval_ms = 100  # Interval (in milliseconds) for latency monitoring
    # threading.Thread(target=monitor_latency, args=(h1, h4, latency_interval_ms, 'latency_h1_h4.csv')).start()
    # threading.Thread(target=monitor_latency, args=(h2, h5, latency_interval_ms, 'latency_h2_h5.csv')).start()

    latency_process = Process(target=monitor_latency, args=(h1, h4, interval_ms, 'latency_h1_h4.csv'))
    latency_process = Process(target=monitor_latency, args=(h2, h5, interval_ms, 'latency_h2_h5.csv'))
    
    # Monitor throughput on each host
    throughput_interval_s = 1  # Interval (in seconds) for throughput monitoring
    # threading.Thread(target=monitor_throughput, args=(h1, 'throughput_h1.csv', throughput_interval_s)).start()
    # threading.Thread(target=monitor_throughput, args=(h2, 'throughput_h2.csv', throughput_interval_s)).start()
    # threading.Thread(target=monitor_throughput, args=(h3, 'throughput_h3.csv', throughput_interval_s)).start()
    # threading.Thread(target=monitor_throughput, args=(h4, 'throughput_h4.csv', throughput_interval_s)).start()
    # threading.Thread(target=monitor_throughput, args=(h5, 'throughput_h5.csv', throughput_interval_s)).start()

    throughput_process = Process(target=monitor_throughput, args=(h1, 'throughput_h1.csv', throughput_interval_s))
    throughput_process = Process(target=monitor_throughput, args=(h2, 'throughput_h2.csv', throughput_interval_s))
    throughput_process = Process(target=monitor_throughput, args=(h3, 'throughput_h3.csv', throughput_interval_s))
    throughput_process = Process(target=monitor_throughput, args=(h4, 'throughput_h4.csv', throughput_interval_s))
    throughput_process = Process(target=monitor_throughput, args=(h5, 'throughput_h5.csv', throughput_interval_s))

    # Iniciar processos
    flow_process.start()
    elephant_process.start()
    latency_process.start()
    throughput_process.start()

    # Esperar todos os processos terminarem
    flow_process.join()
    elephant_process.join()
    latency_process.join()
    throughput_process.join()   
    

     # Plot latency and throughput after the experiment
    plot_latency('latency_h1_h4.csv')
    plot_latency('latency_h2_h5.csv')
    plot_throughput('throughput_h1.csv')
    plot_throughput('throughput_h2.csv')
    plot_throughput('throughput_h3.csv')
    plot_throughput('throughput_h4.csv')
    plot_throughput('throughput_h5.csv')   


    
    # CLI for interactive control
    CLI(net)
    
    # Stop the network
    net.stop()



    