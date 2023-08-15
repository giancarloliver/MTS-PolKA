#!/bin/bash

# Definir as variáveis de configuração
IPERF_SERVER="10.0.2.2"  # Substitua pelo endereço IP do servidor iperf3
# PACKET_COUNT=10000

# Loop para enviar os pacotes UDP individualmente

iperf3 -c $IPERF_SERVER -u -b 10M -n 100000000

