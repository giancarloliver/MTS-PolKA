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

n_switches_E = 2
n_switches_C_N1 = 2
n_switches_C_N2 = 5
BW = 100
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
    # net.addLink(switches_n1[1], edges[3], bw=BWE)
    # net.addLink(switches_n1[1], edges[4], bw=BWE) 

    # net.addLink(switches_n2[2], edges[2], bw=BWE) 

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

    h1, h2 = net.get('h1', 'h2')    

    samples = 30
    test = 1

    for j in range(samples):
        
        print(f"Running Test {test}")   
        start_time = time.time()
        print(f"Starting Time: {start_time:.2f} seconds")             

        ### Definicao nome arquivo bwm-ng
        arq_bwm = f"data/run2/{test}-tmp.bwm"

        ### Definicao do monitor de vazao
        monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))          

        ### Chamada da funcao de monitoramento de pacotes de rede
        print("Start iperf server")

        ### Iniciando o iperf server nos hosts h2 e h4
        h2.cmd('iperf3 -s &')
       

        ### Inciando captura dos dados com bwm-ng
        print(f"Iniciando bwm-ng")
        monitor_cpu.start()
        time.sleep(1) 


        # Start the iperf client on h1
        iperf_cmd = f'iperf3 -u -c {h2.IP()} -t 35 -b 10M'
        h1.cmd(iperf_cmd + ' &')
        time.sleep(1)

        profiles = [
            (0, "1","2","1","00:00:00:00:02:02", "37968085910475", "0", 50101),
            (4, "1","2","1","00:00:00:00:02:02", "201075362587017487558704", "79664158660626060758226", 50101),
            (11, "1","2","1","00:00:00:00:02:02", "73817044396459291349659850249", "37823969743312635090392551816", 50101)
        ]
        
        for profile, idx, port, sr, mac, field1, field2, thrift_port in profiles:
            # Modify the P4 table with profile information
            command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header {idx} {port} {sr} {mac} {field1} {field2}" | simple_switch_CLI --thrift-port {thrift_port}'
            subprocess.run(command, shell=True)
            # Aguardar um tempo para que a tabela seja atualizada antes de executar o teste
            print(f"Aguardar para o teste do perfil {profile} durante 10 segundos")
            time.sleep(10)      
                  
          
        # Stop iperf and bwm-ng
        print("Stop iperf3 e bwm-ng")
        os.system("killall iperf3")
        os.system("killall bwm-ng")
        
        #os.system(f"cat data/run6/{test}-tmp.bwm >> {bwm_file}")        
        os.system(f"grep 's2_0-eth2' data/run/{test}-tmp.bwm > data/run/s2_0-a{test}.csv")        
        os.system(f"grep 's2_2-eth2' data/run/{test}-tmp.bwm > data/run/s2_2-a{test}.csv")        
        os.system(f"grep 's1_1-eth1' data/run/{test}-tmp.bwm > data/run/s1_1-a{test}.csv")           
        time.sleep(1)  
        
        end_time = time.time()
        print(f"End Time: {end_time:.2f} seconds")
        total_execution_time = end_time - start_time
        print(f"Total Execution Time: {total_execution_time:.2f} seconds")

        test = test + 1       

    info("*** Stopping network\n")
    net.stop()