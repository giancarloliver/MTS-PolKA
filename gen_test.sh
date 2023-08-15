#!/bin/bash

declare -g IP_RECEIVER="10.0.2.2"
declare -g IPERFTIME=120
declare -g SLEEPTIME=30
declare -g DELAY=2
declare -g SAMPLES=3




start_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Test started at: $start_time"

sleep 2
# Iniciar captura de tráfego com bwm-ng
echo "Starting traffic capture with bwm-ng..."
bwm-ng -t 1000 -o csv -u bytes-T rate -C ',' > capture_results.csv &
bwm_pid=$!

sleep 1

echo "teste do perfil 11"
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 73817044396459291349659850249 37823969743312635090392551816" | simple_switch_CLI --thrift-port 50101
# echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101
echo "Aguardar para o teste do perfil 11 durante 10  segundos"

sleep 10

echo "teste do perfil 4"
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 201075362587017487558704 79664158660626060758226" | simple_switch_CLI --thrift-port 50101
# echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101
echo "Aguardar para o teste do perfil 4 durante 10  segundos"
sleep 10

echo "teste do perfil"
echo "table_modify tunnel_encap_process_sr add_sourcerouting_header 1  2 1 00:00:00:00:02:02 37968085910475 0" | simple_switch_CLI --thrift-port 50101
# echo "table_dump_entry_from_key MyIngress.process_tunnel_encap.tunnel_encap_process_sr 10.0.2.2/32 " | simple_switch_CLI --thrift-port 50101
echo "Aguardar para o teste do perfil 0 durante 10  segundos"
sleep 10

end_time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Test ended at: $end_time"

# # Adicionar os tempos de início e término ao arquivo de resultados
echo "Start Time: $start_time" >> capture_results.csv
echo "End Time: $end_time" >> capture_results.csv

# Stopping the packet capture and iperf3 server processes
killall bwm-ng
killall iperf


