import socket
import time
import csv

# Definir o endere�o IP e porta do servidor
server_ip = '10.0.2.2'
server_port = 12345

# Criar um socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definir o endere�o IP e porta do cliente
client_ip = '10.0.1.1'
client_port = 54321
client_address = (client_ip, client_port)

# Vincular o socket do cliente ao endere�o IP e porta do cliente
client_socket.bind(client_address)

# Configurar o contador e o tempo inicial
count = 0
start_time = time.time()

# Abrir o arquivo CSV para escrita
csv_file = open('vazao_rede.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Tempo (s)', 'Pacotes Enviados', 'Vazao (pacotes/s)'])

# Enviar 10000 pacotes UDP
while count < 10000:
    message = f'Mensagem {count}'
    client_socket.sendto(message.encode(), (server_ip, server_port))
    count += 1

# Calcular a vaz�o de rede
end_time = time.time()
elapsed_time = end_time - start_time
vazao = count / elapsed_time

# Salvar as informa��es de vaz�o no arquivo CSV
csv_writer.writerow([elapsed_time, count, vazao])
csv_file.close()

# Fechar o socket do cliente
client_socket.close()