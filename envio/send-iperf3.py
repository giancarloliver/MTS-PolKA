#!/usr/bin/env python3
import argparse
import subprocess
import os
import time
from multiprocessing import Process
from subprocess import Popen
from time import sleep




def main():
    parser = argparse.ArgumentParser(description="Send UDP packets using iperf3")
    parser.add_argument("destination", type=str, help="Destination IP address")
    parser.add_argument("message", type=str, help="Message to send")
    parser.add_argument("-t", "--time", type=int, default=10, help="Time duration in seconds (default: 10)")
    args = parser.parse_args()
 
       
    # Run iperf3 client in UDP mode with specified time and bandwidth
    iperf_client_cmd = f"iperf3 -c {args.destination} -u -b 10M -t {args.time}"
    subprocess.run(iperf_client_cmd, shell=True, input=args.message.encode())

    os.system("killall bwm-ng")

if __name__ == '__main__':
    main()
