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


def execute_bwm_ng(interface):
    command = f"bwm-ng -I {interface} -t 1000 -o csv -u bytes > {interface}.csv"
    print(f"Executing command: {command}")

    # Execute the command in a subprocess
    subprocess.Popen(command, shell=True)


# def execute_bwm_ng(interface):
#     command = f"bwm-ng -t 1000 -I {interface} -o csv -u bytes -T rate -C ','"
#     output_file = f"{interface}.csv"
#     print(f"Executing command: {command}")

#     # Execute the command and redirect the output to a file
#     with open(output_file, "w") as file:
#         subprocess.run(command, shell=True, stdout=file)

# def execute_bwm_ng(interface):
#     command = f"bwm-ng -t 1000 -I {interface} -o csv -u bytes -T rate -C ',' > {interface}.csv"
#     print(f"Executing command: {command}")

    # # Execute the command in a subprocess
    # subprocess.Popen(command, shell=True)

def send_packets(addr, iface, message):
    # Enviar 10000 paquetes UDP
    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / message
        sendp(pkt, iface=iface, verbose=False)

def main():
    if len(sys.argv) < 3:
        print('Provide 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("Sending on interface %s to %s" % (iface, str(addr)))

    # Execute bwm-ng for each interface in a separate thread
    interfaces = ["s1-eth2", "s1-eth4", "s1-eth6", "s2-eth2", "s4-eth2", "s6-eth2", "s7-eth1"]
    bwm_threads = [] 

    
    for interface in interfaces:
        thread = threading.Thread(target=execute_bwm_ng, args=(interface,))
        thread.start()
        bwm_threads.append(thread)

    # Start iperf3 in the background to generate flow
    iperf_cmd = 'iperf3 -c {0} -t 60 -u -b 10m 1 | awk \'{{gsub(/ /, ","); print}}\' > resultado.csv'.format(addr)
    iperf_process = subprocess.Popen(iperf_cmd, shell=True)

    # Send UDP packets in a separate thread
    send_thread = threading.Thread(target=send_packets, args=(addr, iface, sys.argv[2]))
    send_thread.start()
    
   

    # Wait for the packet sending to complete
    send_thread.join()

    # Terminate iperf3 process
    subprocess.run(["killall", "iperf3"])

    # Wait for bwm-ng threads to complete
    for thread in bwm_threads:
        thread.join()

    # Terminate bwm-ng processes
    subprocess.run(["killall", "bwm-ng"])

if __name__ == '__main__':
    main()
