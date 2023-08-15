#!/bin/bash

IP_RECEIVER="10.0.2.2"  # Endereço IP do host que receberá os pacotes UDP
IP_SENDER="10.0.1.1"  # Endereço IP do host que enviará os pacotes UDP
IPERFTIME=10  # Tempo máximo em segundos para o iperf3 rodar
BANDWIDTH="10"  # Largura de banda em Mbps
SLEEPTIME=5  # Tempo de espera em segundos
NUM_PACKAGES=10000  # Número de pacotes a serem enviados

# Iniciar o servidor iperf3 no host receptor (10.0.2.2)
iperf_server_cmd="iperf3 -s"
ssh $IP_RECEIVER $iperf_server_cmd &

# Aguardar um tempo para garantir que o servidor esteja ativo
sleep $SLEEPTIME

# Capturar pacotes de todas as interfaces do dispositivo Mininet
capture_packets() {
    bwmng_cmd="bwm-ng -t 1000 -o csv -u packets -T rate -C ',' > all_interfaces.bwm &"
    eval $bwmng_cmd
}

# Capturar pacotes de todas as interfaces do dispositivo Mininet
capture_packets

# Aguardar o tempo necessário para o teste
sleep $SLEEPTIME

# Enviar os pacotes UDP em um loop
PACKET_SIZE=1000  # Tamanho do pacote UDP em bytes
NUM_SENT_PACKAGES=100  # Número de pacotes enviados
while [ $NUM_SENT_PACKAGES -lt $NUM_PACKAGES ]; do
    remaining_packages=$((NUM_PACKAGES - NUM_SENT_PACKAGES))
    if [ $remaining_packages -lt 1000 ]; then
        PACKET_SIZE=$remaining_packages
    fi

    iperf_cmd="iperf3 -c $IP_RECEIVER -u -b $BANDWIDTH"m" -n $PACKET_SIZE | awk '{gsub(/ /, \",\"); print}' >> resultado.csv"
    ssh $IP_SENDER $iperf_cmd

    NUM_SENT_PACKAGES=$((NUM_SENT_PACKAGES + PACKET_SIZE))
done

# Encerrar os processos de captura de pacotes em cada dispositivo do Mininet
for device in "${devices[@]}"; do
    killall bwm-ng
done

# Encerrar o servidor iperf3 no host receptor (10.0.2.2)
killall iperf3
