#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import os
import re


from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP, TCP


def get_if():
    ifs = get_if_list()
    mininet_ifs = [iface for iface in ifs if re.match(r"s\d+-eth\d+", iface)]
    if not mininet_ifs:
        print("No Mininet interfaces found (sX-ethX)")
        exit(1)
    return mininet_ifs


def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])

    interfaces = get_if()
    print("Sending on interfaces: %s to %s" % (', '.join(interfaces), str(addr)))

    # Execute bwm-ng in the background to monitor the interfaces
    bwm_cmd = 'bwm-ng -t 1000 -I "{0}" -o csv -u packets -T rate -C "," >> bwm_output0.bwm &'.format(','.join(interfaces))
    bwm_process = subprocess.Popen(bwm_cmd, shell=True)

    # Execute iperf3 in the background to generate the flow
    iperf_cmd = 'iperf3 -c {0} -u -b 10m | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Send 10000 UDP packets on each Mininet interface
    for interface in interfaces:
        for i in range(10000):
            pkt = Ether(src=get_if_hwaddr(interface), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
            sendp(pkt, iface=interface, verbose=False)

    # Wait for iperf3 to finish
    iperf_process.wait()

    # Wait for bwm-ng to finish
    bwm_process.wait()


if __name__ == '__main__':
    main()
