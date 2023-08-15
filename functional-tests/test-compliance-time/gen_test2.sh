#!/bin/bash

declare -g IP_RECEIVER="10.0.2.2"
declare -g INTERFACE="enp0s8"
declare -g IP="40.40.2.2"
declare -g IPERFTIME=120
declare -g SLEEPTIME=30
declare -g DELAY=2
declare -g SAMPLES=3




start_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Test started at: $start_time"

# # Capturing packets from all interfaces of the device Mininet
# capture_packets() {
#     bwmng_cmd="bwm-ng -t 1000 -o csv -u packets -T rate -C ',' > all_interfaces.bwm &"
#     eval $bwmng_cmd
# }
# sleep 1



echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101

# echo "altering Entry 2 in tunnel_encap_process_sr table"
# echo "table_delete MyIngress.process_tunnel_encap.tunnel_encap_process_sr 1" | simple_switch_CLI --thrift-port 50101
# # # echo "table_set_default tunnel_encap_process_sr add_sourcerouting_header 0 0 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00" | simple_switch_CLI --thrift-port 50101
# # # echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.1.1/32 => 1 0 00:00:00:00:01:01 0 0" | simple_switch_CLI --thrift-port 50101
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 73817044396459291349659850249 37823969743312635090392551816" | simple_switch_CLI --thrift-port 50101
# echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.2.2/32 => 2 1 00:00:00:00:02:02 73817044396459291349659850249 37823969743312635090392551816" | simple_switch_CLI --thrift-port 50101
echo "table_dump  MyIngress.process_tunnel_encap.tunnel_encap_process_sr" | simple_switch_CLI --thrift-port 50101

sleep $SLEEPTIME

echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101

# echo "altering Entry 2 in tunnel_encap_process_sr table"
# echo "table_delete MyIngress.process_tunnel_encap.tunnel_encap_process_sr 1000001" | simple_switch_CLI --thrift-port 50101
# # echo "table_set_default tunnel_encap_process_sr add_sourcerouting_header 0 0 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00" | simple_switch_CLI --thrift-port 50101
# # echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.1.1/32 => 1 0 00:00:00:00:01:01 0 0" | simple_switch_CLI --thrift-port 50101
# echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.2.2/32 => 2 1 00:00:00:00:02:02 201075362587017487558704 661932925562025386441800" | simple_switch_CLI --thrift-port 50101
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 201075362587017487558704 661932925562025386441800" | simple_switch_CLI --thrift-port 50101
echo "table_dump  MyIngress.process_tunnel_encap.tunnel_encap_process_sr" | simple_switch_CLI --thrift-port 50101

sleep $SLEEPTIME


echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101

echo "altering Entry 2 in tunnel_encap_process_sr table again"
echo "table_delete MyIngress.process_tunnel_encap.tunnel_encap_process_sr 1000001" | simple_switch_CLI --thrift-port 50101
# # echo "table_set_default tunnel_encap_process_sr add_sourcerouting_header 0 0 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00" | simple_switch_CLI --thrift-port 50101
# # echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.1.1/32 => 1 0 00:00:00:00:01:01 0 0" | simple_switch_CLI --thrift-port 50101
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 37968085910475 0" | simple_switch_CLI --thrift-port 50101
# echo "table_add tunnel_encap_process_sr add_sourcerouting_header 10.0.2.2/32 => 2 1 00:00:00:00:02:02 37968085910475 0" | simple_switch_CLI --thrift-port 50101
echo "table_dump  MyIngress.process_tunnel_encap.tunnel_encap_process_sr" | simple_switch_CLI --thrift-port 50101

sleep 2

end_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Test ended at: $end_time"

# Stopping the packet capture and iperf3 server processes
killall bwm-ng
killall iperf


