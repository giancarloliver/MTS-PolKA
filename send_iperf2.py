#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import os

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

def get_all_interfaces():
    interfaces = []
    ifs = get_if_list()
    for i in ifs:
        if i != "lo" and "eth" not in i:
            interfaces.append(i)
    return interfaces

def start_bwm_ng(interfaces):
    bwmng_cmd = f"bwm-ng -o csv -c {','.join(interfaces)} -T rate -F resultado_bwmng.csv"
    bwmng_process = subprocess.Popen(bwmng_cmd, shell=True)

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    interfaces = get_all_interfaces()

    print(f"Sending on interface {iface} to {str(addr)}")

    # Start bwm-ng process to capture interface data
    start_bwm_ng(interfaces)

    # Ejecutar iperf3 en segundo plano para generar el flujo
    iperf_cmd = f"iperf3 -c {addr} -u -b 10m 1 | awk '{{gsub(/ /, \",\"); print}}\' > resultado_iperf.csv"
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Enviar 10000 paquetes UDP
    for i in range(10000):
        for interface in interfaces:
            pkt = Ether(src=get_if_hwaddr(interface), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
            sendp(pkt, iface=interface, verbose=False)

    # Esperar a que iperf3 termine
    iperf_process.wait()

    # Terminate the bwm-ng process
    bwmng_process.terminate()
    bwmng_process.wait()

    print("bwm-ng stopped")

if __name__ == '__main__':
    main()
