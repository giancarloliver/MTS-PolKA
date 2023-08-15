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

    # Variables to track time and packets
    start_time = time.time()
    current_time = start_time
    interval = 10  # Time interval in seconds to record compliance time
    packets_sent = 0

    # Enviar 10000 paquetes UDP
    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        sendp(pkt, iface=iface, verbose=False)

        # Increment packets_sent count
        packets_sent += 1

        # Check compliance time and packet count every interval seconds
        if time.time() - current_time >= interval:
            current_time = time.time()
            elapsed_time = current_time - start_time
            print("Compliance time: {:.2f} seconds".format(elapsed_time))
            print("Packets sent: {}".format(packets_sent))

            # Append the compliance time and packet count to the CSV file
            with open('resultado.csv', 'a') as f:
                f.write("{:.2f},{}\n".format(elapsed_time, packets_sent))

            packets_sent = 0  # Reset packet count

    # Wait for the remaining packets to be sent
    remaining_packets = 10000 - (i + 1)
    time.sleep(remaining_packets * 0.001)  # Sleep for remaining packets' transmission time

    # Stop iperf3 and bwm-ng processes
    iperf_process.terminate()
    iperf_process.wait()
    bwmng_process = subprocess.Popen(['pkill', 'bwm-ng'])
    bwmng_process.wait()

    print("bwm-ng stopped")

if __name__ == '__main__':
    main()
