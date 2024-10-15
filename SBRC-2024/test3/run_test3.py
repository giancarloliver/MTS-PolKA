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

import os
import subprocess
import time
from multiprocessing import Process

n_switches_E = 5
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 10
BWE = 100


def monitor_bwm_ng(fname, interval_sec):
    cmd = f"sleep 1; bwm-ng -t {interval_sec * 100} -o csv -u bytes -T rate -C ',' > {fname}"
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

    # Links between hosts and edge switches
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

    h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')    

    samples = 30
    test = 1

    for j in range(samples):
        
        print(f"Running Test {test}")   
        start_time = time.time()
        print(f"Starting Time: {start_time:.2f} seconds")             

        ### Definicao nome arquivo bwm-ng
        arq_bwm = f"data/run/{test}-tmp.bwm"

        ### Definicao do monitor de vazao
        monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))          

        ### Chamada da funcao de monitoramento de pacotes de rede
        print("Start iperf server")

        ### Iniciando o iperf server nos hosts h2 e h4
        h2.cmd('iperf3 -s &')
        h5.cmd('iperf3 -s &')
        h4.cmd('iperf3 -s &')
        time.sleep(1)         
        
        profiles = [
            (0, "1","2","1","00:00:00:00:02:02", "281023905350220", "0", 50101),
            (1, "2","2","1","00:00:00:00:05:05", "9042577315084523862", "7494471750674993136", 50101),
            (2, "1","2","1","00:00:00:00:04:04", "2719489540", "0", 50103)
        ]
        
        for profile, idx, port, sr, mac, field1, field2, thrift_port in profiles:
            # Modify the P4 table with profile information
            command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header {idx} {port} {sr} {mac} {field1} {field2}" | simple_switch_CLI --thrift-port {thrift_port}'
            subprocess.run(command, shell=True)
            # Wait for the table to be updated before executing the test
            time.sleep(1)     
           
        
        # Set TCP window size (adjust as needed)e
        tcp_window_size = "1M" 

        print(f"1 fluxo tcp 1 com origem H1(conectado em s1_0) e dest H2(conectado em s1_1)  com perfil de tráfego 0")
        h1.cmd(f'iperf3 -c {h2.IP()} -t 22 -b -w {tcp_window_size} &')

        print(f"1 fluxo tcp 2 com origem H1(conectado em s1_0) e dest H5(conectado em s1_1)  com perfil de tráfego 1")
        h1.cmd(f'iperf3 -c {h5.IP()} -t 22 -b -w {tcp_window_size} &')
        # tcp_window_size = "1M" 
        # h1.cmd(f'iperf3 -c {h2.IP()} -t 30 &')
        # h1.cmd(f'iperf3 -c {h5.IP()} -t 30 &')
       
        print(f"1 fluxo udp com origem H3(conectado em s2_2) e dest H4(conectado em s1_1)  com perfil de tráfego 1")
        iperf_cmd = f'iperf3 -u -c {h4.IP()} -t 22 -b 4M'
        h3.cmd(iperf_cmd + ' &')   

        ### Inciando captura dos dados com bwm-ng
        print(f"Iniciando bwm-ng")
        monitor_cpu.start()
        time.sleep(1)  
                              
               
        # aguardar 10s
        print(f"Aguardar para o teste inicial durante 10 segundos")
        time.sleep(10)

        # Modify the P4 table with profile information test 3 1-1
        print(f"Migração: fluxo tcp com origem H1 e dest H2 passa para perfil de tráfego 1:1 passando por S2_0 e s2_1")
        command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:02:02 15459190764020546716 14558177261190933974" | simple_switch_CLI --thrift-port 50101'
        subprocess.run(command, shell=True)
        # Wait for the table to be updated before executing the test
                       
        # aguardar 20s
        print(f"Aguardar para o teste inicial durante 25 segundos")
        time.sleep(22)
    
        # Stop iperf and bwm-ng
        print("Stop iperf3 e bwm-ng")
        os.system("killall iperf3")
        os.system("killall bwm-ng")
        
        #os.system(f"cat data/run6/{test}-tmp.bwm >> {bwm_file}")
        os.system(f"grep 's1_0-eth1' data/run/{test}-tmp.bwm > data/run/s1_0-eth1-a{test}.csv")
        os.system(f"grep 's1_0-eth2' data/run/{test}-tmp.bwm > data/run/s1_0-eth2-a{test}.csv") 
        os.system(f"grep 's1_0-eth3' data/run/{test}-tmp.bwm > data/run/s1_0-eth3-a{test}.csv") 
        os.system(f"grep 's1_0-eth4' data/run/{test}-tmp.bwm > data/run/s1_0-eth4-a{test}.csv") 
        os.system(f"grep 's1_0-eth5' data/run/{test}-tmp.bwm > data/run/s1_0-eth5-a{test}.csv") 
        os.system(f"grep 's1_0-eth6' data/run/{test}-tmp.bwm > data/run/s1_0-eth6-a{test}.csv") 
        os.system(f"grep 's2_0-eth2' data/run/{test}-tmp.bwm > data/run/s2_0-eth2-a{test}.csv") 
        os.system(f"grep 's2_1-eth2' data/run/{test}-tmp.bwm > data/run/s2_1-eth2-a{test}.csv")
        os.system(f"grep 's2_2-eth3' data/run/{test}-tmp.bwm > data/run/s2_2-eth3-a{test}.csv")
        os.system(f"grep 's2_3-eth2' data/run/{test}-tmp.bwm > data/run/s2_3-eth2-a{test}.csv")
        os.system(f"grep 's2_4-eth2' data/run/{test}-tmp.bwm > data/run/s2_4-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth1' data/run/{test}-tmp.bwm > data/run/s1_1-eth1-a{test}.csv")
        os.system(f"grep 's1_1-eth2' data/run/{test}-tmp.bwm > data/run/s1_1-eth2-a{test}.csv")
        os.system(f"grep 's1_1-eth3' data/run/{test}-tmp.bwm > data/run/s1_1-eth3-a{test}.csv")       
        time.sleep(1)  
        
        end_time = time.time()
        print(f"End Time: {end_time:.2f} seconds")
        total_execution_time = end_time - start_time
        print(f"Total Execution Time: {total_execution_time:.2f} seconds")

        test = test + 1       

    info("*** Stopping network\n")
    net.stop()