import csv

with open('s1-eth2.csv', 'r') as arquivo:
    leitor = csv.reader(arquivo)
    for linha in linhas:
        colunas = linha.split(",")
        bytes_sent = float(colunas[4])
        bytes_received = float(colunas[5])
        print("bytes_sent:", bytes_sent)
        print("bytes_received:", bytes_received)
        print("---")