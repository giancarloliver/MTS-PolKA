#!/bin/bash

IP_RECEIVER="10.0.2.2"  # IP address of the host that will receive the UDP packets
IP_SENDER="10.0.1.1"  # IP address of the host that will send the UDP packets
IPERFTIME=10  # Maximum time in seconds for iperf3 to run
BANDWIDTH="40"  # Bandwidth in Mbps
SLEEPTIME=5  # Waiting time in seconds
NUM_PACKAGES=10000  # Number of packets to be sent
DELAY=2
SAMPLES=20  # Number of times the test will be performed

# Start iperf3 server on the receiver host (10.0.2.2)
iperf_server_cmd="iperf3 -s"
ssh $IP_RECEIVER $iperf_server_cmd &

# Wait for some time to ensure the server is active
sleep $SLEEPTIME

# Function to capture packets from all interfaces using bwm-ng
capture_packets() {
    bwmng_cmd="bwm-ng -t 1000 -o csv -u bytes -T rate -C ',' > tmp.bwm &"
    eval $bwmng_cmd
}

# Capture packets from all interfaces
capture_packets

# Wait for the required time for the test
sleep $SLEEPTIME

# Function to send UDP packets using iperf3
Iperf_client() {
    FILENAME="$1"
    INTERFACE="$2"
    PACKET_SIZE=1000  # Packet size in bytes
    NUM_SENT_PACKAGES=100000  # Number of packets sent
    iperf_cmd="iperf3 -c $IP_RECEIVER -k $NUM_SENT_PACKAGES -u -b $BANDWIDTH"m" | awk '{gsub(/ /, \",\"); print}' >> resultado.csv"
    ssh $IP_SENDER $iperf_cmd
    killall bwm-ng
    mkdir -p data/run$RUN/$BANDWIDTH
    grep $INTERFACE tmp.bwm > data/run$RUN/$BANDWIDTH/$FILENAME.csv
    rm tmp.bwm
    sleep $DELAY
}

# Define the array of devices for packet capture
devices=("h1" "h2" "e1" "e2" "s1" "s2" "s3" "s4" "s5" "s6" "s7")

for j in 40; do
    echo "Considering a bandwidth of ${j} Mbps"
    for i in $(seq 1 $SAMPLES); do
        start_time=$(date +%s)
        echo "Sample #${i}: Started at: ${start_time}"
        Iperf_client "a${i}" "eth0"
        end_time=$(date +%s)
        echo "Sample #${i}: Finished at: ${end_time}"
    done
done

# Terminate the packet capture processes on each device
for device in "${devices[@]}"; do
    ssh $device killall bwm-ng
done

# Terminate the iperf3 server on the receiver host
ssh $IP_RECEIVER killall iperf3
