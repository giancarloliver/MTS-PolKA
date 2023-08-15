#!/usr/bin/env python3
import subprocess

def start_iperf_server():
    command = "iperf3 -s"  # Run iperf3 server
    subprocess.Popen(command, shell=True)

if __name__ == '__main__':
    start_iperf_server()  # Start iperf3 server