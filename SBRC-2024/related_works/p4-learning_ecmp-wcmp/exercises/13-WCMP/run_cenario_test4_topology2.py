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

# Número de switches e largura de banda
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

    net = Mininet_wifi()

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
        json_file = f"{path}/p4src/wcmp.json"
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
        json_file = f"{path}/p4src/wcmp.json"
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
        json_file = f"{path}/p4src/wcmp.json"
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
    # Links between hosts and edge switches
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
    info("*** Running CLI\n")
    CLI(net)

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()

    
if __name__ == "__main__":
    setLogLevel("info")
    remote_controller = False
    topology(remote_controller)

    # h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')    

    # samples = 30
    # test = 1

    # for j in range(samples):
    #     info(f"Running Test {test}\n")
    #     start_time = time.time()
    #     info(f"Starting Time: {start_time:.2f} seconds\n")             

    #     # Definindo o nome do arquivo bwm-ng
    #     arq_bwm = f"data/run/{test}-tmp.bwm"

    #     # Definindo o monitor de vazão
    #     monitor_cpu = Process(target=monitor_bwm_ng, args=(arq_bwm, 1.0))          

    #     # Iniciando o servidor iperf3 nos hosts h2 e h4
    #     info("Start iperf server\n")
    #     h2.cmd('iperf3 -s &')
    #     h5.cmd('iperf3 -s &')
    #     h4.cmd('iperf3 -s &')
    #     time.sleep(1)      

    #     # Definindo o tamanho da janela TCP
    #     tcp_window_size = "1M" 

    #     info(f"1 fluxo tcp 1 com origem H1 (conectado em s1_0) e dest H2 (conectado em s1_1) com perfil de tráfego 0\n")
    #     h1.cmd(f'iperf3 -c {h2.IP()} -t 22 -b 10M -w {tcp_window_size} &')

    #     info(f"1 fluxo tcp 2 com origem H1 (conectado em s1_0) e dest H5 (conectado em s1_1) com perfil de tráfego 1\n")
    #     h1.cmd(f'iperf3 -c {h5.IP()} -t 22 -b 10M -w {tcp_window_size} &')

    #     info(f"1 fluxo udp com origem H3 (conectado em s2_2) e dest H4 (conectado em s1_1) com perfil de tráfego 1\n")
    #     iperf_cmd = f'iperf3 -c {h4.IP()} -t 22 -b 4M'
    #     h3.cmd(iperf_cmd + ' &')   

    #     # Iniciando captura dos dados com bwm-ng
    #     info(f"Iniciando bwm-ng\n")
    #     monitor_cpu.start()
    #     time.sleep(1)  
                        
    #     # Aguardar 10 segundos
    #     info(f"Aguardar para o teste inicial durante 10 segundos\n")
    #     time.sleep(10)

    #     # # Modificando a tabela P4 com informações do perfil de tráfego
    #     # info(f"Migração: fluxo tcp com origem H1 e dest H2 passa para perfil de tráfego 1:1 passando por S2_0 e s2_1\n")
    #     # command = f'echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1 2 1 00:00:00:00:02:02 15459190764020546716 14558177261190933974" | simple_switch_CLI --thrift-port 50101'
    #     # subprocess.run(command, shell=True)
                       
    #     # Aguardar 25 segundos
    #     info(f"Aguardar para o teste inicial durante 25 segundos\n")
    #     time.sleep(25)
    
    #     # Parar iperf e bwm-ng
    #     info("Stop iperf3 e bwm-ng\n")
    #     os.system("killall iperf3")
    #     os.system("killall bwm-ng")
        
    #     # Processar dados do bwm-ng
    #     os.system(f"grep 's1_0-eth1' data/run/{test}-tmp.bwm > data/run/s1_0-eth1-a{test}.csv")
    #     os.system(f"grep 's1_0-eth2' data/run/{test}-tmp.bwm > data/run/s1_0-eth2-a{test}.csv") 
    #     os.system(f"grep 's1_0-eth3' data/run/{test}-tmp.bwm > data/run/s1_0-eth3-a{test}.csv") 
    #     os.system(f"grep 's1_0-eth4' data/run/{test}-tmp.bwm > data/run/s1_0-eth4-a{test}.csv") 
    #     os.system(f"grep 's1_0-eth5' data/run/{test}-tmp.bwm > data/run/s1_0-eth5-a{test}.csv") 
    #     os.system(f"grep 's1_0-eth6' data/run/{test}-tmp.bwm > data/run/s1_0-eth6-a{test}.csv") 
    #     os.system(f"grep 's2_0-eth2' data/run/{test}-tmp.bwm > data/run/s2_0-eth2-a{test}.csv") 
    #     os.system(f"grep 's2_1-eth2' data/run/{test}-tmp.bwm > data/run/s2_1-eth2-a{test}.csv")
    #     os.system(f"grep 's2_2-eth3' data/run/{test}-tmp.bwm > data/run/s2_2-eth3-a{test}.csv")
    #     os.system(f"grep 's2_3-eth2' data/run/{test}-tmp.bwm > data/run/s2_3-eth2-a{test}.csv")
    #     os.system(f"grep 's2_4-eth2' data/run/{test}-tmp.bwm > data/run/s2_4-eth2-a{test}.csv")
    #     os.system(f"grep 's1_1-eth1' data/run/{test}-tmp.bwm > data/run/s1_1-eth1-a{test}.csv")
    #     os.system(f"grep 's1_1-eth2' data/run/{test}-tmp.bwm > data/run/s1_1-eth2-a{test}.csv")
    #     os.system(f"grep 's1_1-eth3' data/run/{test}-tmp.bwm > data/run/s1_1-eth3-a{test}.csv")       
    #     time.sleep(1)  
        
    #     end_time = time.time()
    #     info(f"End Time: {end_time:.2f} seconds\n")
    #     total_execution_time = end_time - start_time
    #     info(f"Total Execution Time: {total_execution_time:.2f} seconds\n")

    #     test += 1       

    # info("*** Stopping network\n")
    # net.stop()