#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess

from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP

def get_if():
    ifs = get_if_list()
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def get_switch_ifs():
    # Retrieve all interface names of switches in Mininet
    switch_ifs = []
    output = subprocess.check_output(['sudo', 'mn', '-c'], universal_newlines=True)
    lines = output.splitlines()
    for line in lines:
        if line.startswith('switch'):
            switch_name = line.split(':')[0]
            switch_ifs.append(switch_name)
    return switch_ifs

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    switch_ifs = get_switch_ifs()

    print("Sending on interface %s to %s" % (iface, str(addr)))

    # Start bwm-ng command to analyze network traffic on switch interfaces
    for switch_iface in switch_ifs:
        bwm_cmd = 'bwm-ng -o csv -u packets -T rate -C "," -I {0} >> bwm_output0.bwm &'.format(switch_iface)
        os.system(bwm_cmd)

    # Execute iperf3 in the background to generate the flow
    iperf_cmd = 'iperf3 -c {0} -u -b 10m 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Send 1000 UDP packets
    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        sendp(pkt, iface=iface, verbose=False)

    # Wait for iperf3 to finish
    iperf_process.wait()

    # Stop bwm-ng
    os.system('pkill bwm-ng')
    print("bwm-ng stopped")

if __name__ == '__main__':
    main()
