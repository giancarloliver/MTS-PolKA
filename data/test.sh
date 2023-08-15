#!/bin/bash

IP_RECEIVER="endereço_da_máquina_que_vai_receber_os_pacotes"
IP_SENDER="endereço_da_máquina_que_vai_enviar_os_pacotes"
IPERFTIME=10  # Tempo máximo em segundos para o iperf3 rodar
BANDWIDTH=10  # Largura de banda em Mbps
SLEEPTIME=5  # Tempo de espera em segundos
NUM_PACKAGES=10000  # Número de pacotes a serem enviados

# Iniciar o servidor iperf3 na máquina de recebimento
iperf_server_cmd="iperf3 -s -u"
$iperf_server_cmd &

# Capturar os pacotes da rede usando o bwm-ng em cada dispositivo do Mininet
capture_packets() {
    device=$1
    bwmng_cmd="bwm-ng -t 1000 -o csv -u packets -T rate -C ',' > ${device}.bwm &"
    $bwmng_cmd
}

# Capturar pacotes de todos os dispositivos do Mininet
# Substitua os nomes dos dispositivos (s1, s2, h1, h2, etc.) pelos nomes reais em seu cenário
devices=("s1" "s2" "h1" "h2")
for device in "${devices[@]}"; do
    capture_packets $device
done

# Aguardar o tempo necessário para o teste
sleep $SLEEPTIME

# Executar o iperf3 para gerar o fluxo de pacotes UDP
iperf_cmd="iperf3 -c $IP_RECEIVER -u -b ${BANDWIDTH}m -n $NUM_PACKAGES -B $IP_SENDER | awk '{gsub(/ /, \",\"); print}' > resultado.csv"
$iperf_cmd

# Encerrar os processos de captura de pacotes em cada dispositivo do Mininet
for device in "${devices[@]}"; do
    killall bwm-ng
done

# Encerrar o processo do servidor iperf3 na máquina de recebimento
killall iperf3
