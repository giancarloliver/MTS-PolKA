#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import os
import time

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

def measure_compliance_time(start_time, packets_sent):
    elapsed_time = time.time() - start_time
    print(f"Compliance Time: {elapsed_time} seconds")
    transmission_rate = (packets_sent * 8) / elapsed_time  # Calcula a taxa de transmissão em Mbps
    print(f"Transmission Rate: {transmission_rate} Mbps")

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("Sending on interface %s to %s" % (iface, str(addr)))

    # Ejecutar iperf3 en segundo plano para generar el flujo
    iperf_cmd = 'iperf3 -c {0}  -u -b 10m 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    compliance_start_time = time.time()
    packets_sent = 0

    # Enviar 10000 paquetes UDP
    for i in range(10000):
        if (i+1) % 1000 == 0:
            measure_compliance_time(compliance_start_time, packets_sent)

        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        sendp(pkt, iface=iface, verbose=False)

        packets_sent += 1

    measure_compliance_time(compliance_start_time, packets_sent)

    # Esperar a que iperf3 termine
    iperf_process.wait()

    # # Encerrar o processo bwm-ng
    # bwmng_process = subprocess.Popen(['pkill', 'bwm-ng'])
    # bwmng_process.wait()

    # print("bwm-ng stopped")

    # Save packet count to the output file
    with open("resultado2.csv", "a") as file:
        file.write(f"Packets Sent: {packets_sent}\n")

if __name__ == '__main__':
    main()