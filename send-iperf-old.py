#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import iperf3

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

client = iperf3.Client()
client.duration = 1
client.server_hostname = '10.0.2.2'
client.port = 1234
client.protocol = 'udp'

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

def run_iperf():
    # Run iperf command as a subprocess and capture the output
    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    result = client.run()
    if result.error:
        print(result.error)
    else:
        print('')
        print('Test completed:')
        print('  started at         {0}'.format(result.time))
        print('  bytes transmitted  {0}'.format(result.bytes))
        print('  jitter (ms)        {0}'.format(result.jitter_ms))
        print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

        print('Average transmitted data in all sorts of networky formats:')
        print('  bits per second      (bps)   {0}'.format(result.bps))
        print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
        print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
        print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
        print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))
        

def main():
    if len(sys.argv) < 3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))

    for i in range(10):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)

    run_iperf()

if __name__ == '__main__':
    main()
