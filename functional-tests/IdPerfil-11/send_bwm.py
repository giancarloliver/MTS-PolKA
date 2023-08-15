#!/usr/bin/env python3

import subprocess

def start_bwm_ng(interface):
    cmd = ['bwm-ng', '-o', 'csv', '-c', interface, '-T', 'rate', '-F', f'resultado_bwmng_{interface}.csv']
    subprocess.Popen(cmd)

def main():
    # Specify the interfaces you want to capture data from
    interfaces = ['eth1', 'eth2', 'eth3']

    # Start bwm-ng for each interface
    for interface in interfaces:
        start_bwm_ng(interface)

    # Add your code here to perform other operations or generate network traffic

if __name__ == '__main__':
    main()
