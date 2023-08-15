import socket
import csv
import wand

# Definir o endere�o IP e porta do servidor
server_ip = '10.0.2.2'
server_port = 12345

# Criar um socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Vincular o socket do servidor ao endere�o IP e porta do servidor
server_address = (server_ip, server_port)
server_socket.bind(server_address)

# Abrir o arquivo CSV para escrita
csv_file = open('vazao_rede_servidor.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Pacotes Recebidos'])

# Definir o n�mero total de pacotes a serem recebidos
total_packets = 10000

# Inicializar o contador de pacotes recebidos
received_packets = 0

# Receber os pacotes UDP
while received_packets < total_packets:
    data, address = server_socket.recvfrom(1024)
    received_packets += 1

    # Registrar o n�mero de pacotes recebidos no arquivo CSV
    csv_writer.writerow([received_packets])

# Fechar o arquivo CSV
csv_file.close()

# Fechar o socket do servidor
server_socket.close()
