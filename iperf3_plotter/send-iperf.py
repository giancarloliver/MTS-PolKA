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

def main():
    if len(sys.argv) < 3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))

    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)

    command = ['iperf3', '-c', '10.0.2.2', '-u', '-J', '-t', '150', '-C ',',']
    with open('test_results.json', 'w') as f:
        subprocess.run(command, stdout=f)

if __name__ == '__main__':
    main()
