import csv
import matplotlib.pyplot as plt
from datetime import datetime

vazao = []
tempo = []

with open('s1-eth2.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) < 3:
            continue

        # Verificar se o valor de tempo é um número válido
        try:
            timestamp = float(row[0])
            datetime.fromtimestamp(timestamp)
        except (ValueError, OverflowError):
            print(f"Valor inválido de tempo: {row[0]}")
            continue

        # Verificar se o valor de vazão é um número válido
        try:
            valor_vazao = float(row[2].replace(',', '.'))
        except ValueError:
            print(f"Valor inválido de vazão: {row[2]}")
            continue

        vazao.append(valor_vazao)
        tempo.append(timestamp)

plt.plot(tempo, vazao)
plt.xlabel('Tempo')
plt.ylabel('Vazão')
plt.title('Gráfico de Vazão da Rede ao longo do Tempo')
plt.xticks(rotation=45)
plt.show()
