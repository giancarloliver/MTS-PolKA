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

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("Sending on interface %s to %s" % (iface, str(addr)))

    # # Ejecutar iperf3 en segundo plano para generar el flujo
    # iperf_cmd = 'iperf3 -c {0} -t 60 -b 10M 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    # iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Enviar 10000 paquetes UDP
    for i in range(1000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        sendp(pkt, iface=iface, verbose=False)

    # # Esperar a que iperf3 termine
    # iperf_process.wait()

   # Encerrar o processo bwm-ng
    bwmng_process = subprocess.Popen(['pkill', 'bwm-ng'])
    bwmng_process.wait()

    print("bwm-ng stopped")

if __name__ == '__main__':
    main()
