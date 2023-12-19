import matplotlib.pyplot as plt
import numpy as np  # Adicione esta linha

run=1
test = 1
taxa = 100
#csv output format: Type rate:
#unix timestamp;iface_name;bytes_out/s;bytes_in/s;bytes_total/s;bytes_in;bytes_out;packets_out/s;packets_in/s;packets_total/s;packets_in;packets_out;errors_out/s;errors_in/s;errors_in;errors_out\n

plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)

x = []
y = [[],[],[],[],[],[]]
cy = 0
for rtr in range(2, 8):
    x = []
    for sample in range(1, 31):
        arq = f"data/run/s{rtr}-a{sample}.csv"
        print(arq)
        try:
            with open(arq, 'r') as f:
                linhas = f.readlines()

                cont = 1
                for dado in linhas:
                    if sample == 1:
                        x.append(cont)
                        y[rtr - 2].append([])

                    b = dado.split(',')[2]
                    fb = float(b) / 1024 / 1024 * 8
                    y[rtr - 2][cont - 1].append(fb)
                    cont += 1
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {arq}")
	


# Plotagem dos gráficos
cores = ['red', 'yellow', 'green', 'pink', 'orange', 'blue']
for rtr in range(2, 8):
    m = [np.mean(dados) for dados in y[rtr - 2]]
    m_mbps = [valor / 1e6 for valor in m]  # Converter para Mbps
    plt.plot(x, m, linewidth=2, marker='o', markersize=3, color=cores[rtr - 2])

# Configurações finais do gráfico
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (Mbps)')
plt.title(f'Reação da migração de perfis')
plt.tight_layout()  # Adicione esta linha para ajuste automático do layout

plt.savefig(f'data/run/{taxa}.png')
plt.clf()

print(f'a{sample}: OK')