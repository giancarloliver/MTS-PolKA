#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import subprocess
import csv

from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP

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

def main():
    if len(sys.argv) < 3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))

    for i in range(10000):
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=addr) / UDP(dport=1234, sport=random.randint(49152, 65535)) / sys.argv[2]
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)

    iperf_command = ['iperf', '-c', '10.0.2.2', '-i', '1', '-t', '130', '-y', 'C', '-u']
    iperf_output = subprocess.run(iperf_command, capture_output=True, text=True)

    if iperf_output.returncode == 0:
        output_lines = iperf_output.stdout.splitlines()
        if len(output_lines) >= 3:
            header_line = output_lines[1].split(',')
            data_line = output_lines[2].split(',')

            # Extrair os dados relevantes
            iperf_data = [
                data_line[1],  # Endereço IP ou interface de origem
                data_line[2],  # Taxa de bytes enviados por segundo
                data_line[3],  # Taxa de bytes recebidos por segundo
                data_line[4],  # Taxa total de bytes por segundo
                data_line[5],  # Total de bytes recebidos
                data_line[6],  # Total de bytes enviados
                data_line[7],  # Taxa de pacotes enviados por segundo
                data_line[8],  # Taxa de pacotes recebidos por segundo
                data_line[9],  # Taxa total de pacotes por segundo
                data_line[10],  # Total de pacotes recebidos
                data_line[11],  # Total de pacotes enviados
                data_line[12],  # Taxa de erros de envio por segundo
                data_line[13],  # Taxa de erros de recebimento por segundo
                data_line[14],  # Total de erros de recebimento
                data_line[15],  # Total de erros de envio
            ]

            # Escrever os dados no arquivo CSV
            with open('iperf_output.csv', 'w', newline='') as arquivo_csv:
                writer = csv.writer(arquivo_csv)
                writer.writerow(header_line)  # Escrever a linha de cabeçalho
                writer.writerow(iperf_data)  # Escrever os dados

            print("Arquivo CSV gerado com sucesso.")
        else:
            print("Erro: Formato de saída do iperf inválido.")
    else:
        print("Erro: Ocorreu um erro ao executar o comando iperf.")
        print("Mensagem de erro:", iperf_output.stderr)

if __name__ == '__main__':
    main()
