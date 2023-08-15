#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import threading

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

def send_packets(addr, iface, message):
    # Enviar 10000 paquetes UDP
    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / message
        sendp(pkt, iface=iface, verbose=False)

# def main():
#     if len(sys.argv) < 3:
#         print('Provide 2 arguments: <destination> "<message>"')
#         exit(1)

#     addr = socket.gethostbyname(sys.argv[1])
#     iface = get_if()

#     print("Sending on interface %s to %s" % (iface, str(addr)))

#     # Ejecutar iperf3 en segundo plano para generar el flujo
#     iperf_cmd = 'iperf3 -c {0} -t 60 -u -b 10m 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
#     iperf_process = subprocess.Popen(iperf_cmd, shell=True)

#     # Start bwm.py script in the background
#     bwm_process = subprocess.Popen(["python3", "bwm.py"])

#     # Send UDP packets in a separate thread
#     send_thread = threading.Thread(target=send_packets, args=(addr, iface, sys.argv[2]))
#     send_thread.start()

#     # Wait for the packet sending to complete
#     send_thread.join()

#     # Terminate iperf3 and bwm-ng processes
#     subprocess.run(["killall", "iperf3"])
#     subprocess.run(["killall", "bwm-ng"])

# #     # Wait for bwm.py script to complete
# #     bwm_process.wait()

# if __name__ == '__main__':
#     main()

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("Sending on interface %s to %s" % (iface, str(addr)))

    # Ejecutar iperf3 en segundo plano para generar el flujo
    iperf_cmd = 'iperf3 -c {0} -t 60 -u -b 10m 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Start bwm.py script in the background
    bwm_process = subprocess.Popen(["python3", "bwm.py"])

    # Send UDP packets in a separate thread
    send_thread = threading.Thread(target=send_packets, args=(addr, iface, sys.argv[2]))
    send_thread.start()

    # Wait for the packet sending to complete
    send_thread.join()

    # Terminate iperf3 process
    subprocess.run(["killall", "iperf3"])

    # Wait for bwm.py script to complete
    bwm_process.wait()

    # Terminate bwm-ng processes
    subprocess.run(["killall", "bwm-ng"])

if __name__ == '__main__':
    main()
