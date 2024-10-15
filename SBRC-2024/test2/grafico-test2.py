import matplotlib.pyplot as plt
import numpy as np  # Adicione esta linha

run=1
test = 2
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
sw = [2, 4, 7]
swn = [ 'S2_0', 'S2_2', 'S1_1' ]
for rtr, rtn in zip(sw, swn):
    x = []
    for sample in range(1, 31):
        ignorar = 12 # ignorando os primeiros 5s para estabilizar a rede
        max_linhas = 287 # 30s * 10 (amostras / segundo)
        arq = f"data/run/{rtn}-a{sample}.csv"
        print(arq)
        try:
            with open(arq, 'r') as f:
                linhas = f.readlines()

                cont = 1
                for dado in linhas:
                    if ignorar == 0:
                        if cont < (max_linhas -1):
                            if sample == 1:
                                x.append(cont)
                                y[rtr - 2].append([])

                            b = dado.split(',')[2]
                            fb = float(b) / 1024 / 1024 * 8
                            y[rtr - 2][cont - 1].append(fb)
                            cont += 1
                    else:
                        ignorar -= 1
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {arq}")

# Define the colors for each SW value
cores = ['gray', 'orange', 'red']

# Define a variável legend_title
legend_title = 'Switches'

# Ajuste da escala do eixo x para representar corretamente o intervalo de tempo
x = [val * 0.1 for val in x]

# Plotagem dos gráficos
for rtr, nome, cor in zip(sw, swn, cores):
    m = [np.mean(dados) for dados in y[rtr - 2]]
    m_mbps = [valor / 1e6 for valor in m]  # Converter para Mbps
    plt.plot(x, m, linewidth=1, marker='o', markersize=2, color=cor, label=nome)

# Vertical lines at seconds 10, 20, and 30 without labels
plt.axvline(x=10, color='gray', linestyle='--', linewidth=0.5)
plt.axvline(x=20, color='gray', linestyle='--', linewidth=0.5)
plt.axvline(x=30, color='gray', linestyle='--', linewidth=0.5)


# Salvar o gráfico
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (Mbps)')
plt.title(f'Reação da migração de perfis')
plt.tight_layout()
plt.legend(title=legend_title,loc='upper left', bbox_to_anchor=(0.7, 0.9), fontsize=15)
plt.savefig(f'result/test{test}.png')
plt.clf()

print(f'a{sample}: OK')