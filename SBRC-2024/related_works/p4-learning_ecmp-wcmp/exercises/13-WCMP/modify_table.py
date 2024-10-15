#!/usr/bin/env python3
import subprocess
import time
import threading

# Lista de endereços MAC e valores de next_hop
mac_addresses = [
    '00:00:04:02:00:01',
    '00:00:04:02:00:02',
    '00:00:04:02:00:03',
    '00:00:04:02:00:04',
    '00:00:04:02:00:05',
    '00:00:04:02:00:06',
    '00:00:04:02:00:07',
    '00:00:04:02:00:08',
    '00:00:04:02:00:09'
]

next_hops = [3, 3, 3, 4, 4, 4, 5, 5, 5]

# Verifica se as listas têm o mesmo comprimento
if len(mac_addresses) != len(next_hops):
    raise ValueError("As listas de endereços MAC e next_hops devem ter o mesmo comprimento.")

# Base command for modifying the table
base_command = 'echo "table_modify MyIngress.wcmp_group_to_nhop MyIngress.set_nhop {index} {mac} {next_hop}" | simple_switch_CLI --thrift-port 9092'

# Função para executar o tcpdump
def run_tcpdump():
    tcpdump_command = 'sudo tcpdump -xxx -r s1_1-eth1.pcap'
    try:
        # Executa o tcpdump e captura a saída
        result = subprocess.run(tcpdump_command, shell=True, check=True, text=True, capture_output=True)
        print(f"Output do tcpdump:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar tcpdump:\n{e.stderr}")

# Medir o tempo de execução
start_time = time.time()

# Inicia o tcpdump em um thread separado
tcpdump_thread = threading.Thread(target=run_tcpdump)
tcpdump_thread.start()

# Loop para criar e executar comandos para cada valor
for i in range(len(mac_addresses)):
    mac = mac_addresses[i]
    next_hop = next_hops[i]
    
    # Constrói o comando completo
    command = base_command.format(index=i, mac=mac, next_hop=next_hop)
    
    try:
        # Executa o comando e verifica se ocorreu um erro
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"Executado: {command}")
        print(f"Saída: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {command}")
        print(f"Erro: {e.stderr}")

# Executar o script send.py
destination_ip = "10.0.2.2"  # Substitua pelo IP de destino real
packet_count = 1000  # Substitua pelo número de pacotes desejado

send_command = f"./send.py {destination_ip} {packet_count}"
try:
    send_result = subprocess.run(send_command, shell=True, check=True, text=True, capture_output=True)
    print(f"Executado: {send_command}")
    print(f"Saída: {send_result.stdout}")
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar: {send_command}")
    print(f"Erro: {e.stderr}")

# Aguarda o término do tcpdump
tcpdump_thread.join()

# Medir o tempo decorrido após a execução do send.py e tcpdump
end_time = time.time()
execution_time = end_time - start_time
print(f"Tempo total de execução: {execution_time:.2f} segundos")
