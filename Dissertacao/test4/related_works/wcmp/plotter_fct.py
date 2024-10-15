import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

run = 1
test = 1
taxa = 10

# Define interfaces and labels
interfaces = ['s1_1-eth1', 's1_1-eth2', 's1_1-eth3']
labels = ['H4 (Mice Flows Destination)', 'H5 (Elephant Flow 1 Destination)', 'H6 (Elephant Flow 2 Destination)']
# Plot settings
plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)

def plot_graph(x, m, interface, color):
    """Plot graph with markers."""
    plt.plot(x, m, linewidth=1, marker='o', markersize=2, color=color, label=interface)

all_x = []
y = [[] for _ in range(len(interfaces))]

# Process files and gather data
for interface_idx, interface in enumerate(interfaces):
    x = []
    for sample in range(1, 2):  # Ajuste conforme necessário para processar mais amostras
        ignorar = 1
        arq = f"data/run/{interface}-a{sample}.csv"
        print(f"Processing file: {arq}")  # Debugging line
        try:
            with open(arq, 'r') as f:
                dados_arq = f.readlines()
                print(f"Total lines read: {len(dados_arq)}")  # Debugging line
                for cont, dado in enumerate(dados_arq, start=1):
                    if ignorar > 0:
                        ignorar -= 1
                    else:
                        x.append(cont)
                        # Lógica para escolher a coluna correta baseado na interface
                        if interface in ['s1_0-eth1', 's1_0-eth2', 's1_0-eth8']:  # Origem (H1 e H2)
                            b = dado.split(',')[3]  # Coluna 4
                        else:  # Destino (H3, H4 e H5)
                            b = dado.split(',')[2]  # Coluna 3
                        fb = float(b) / 1024 / 1024 * 8
                        
                        # Garantir que y[interface_idx] tenha o tamanho necessário
                        while len(y[interface_idx]) < cont:
                            y[interface_idx].append([])

                        y[interface_idx][cont - 1].append(fb)

        except FileNotFoundError:
            print(f"File not found: {arq}")

    all_x.extend(x)
    print(f"Data collected for {interface}: {len(x)} points")  # Debugging line

# Plotting
cores = ['green', 'blue','red','orange', 'brown', 'pink' ]
for interface, color, nome in zip(interfaces, cores, labels):
    m = [np.mean(dados) if dados else np.nan for dados in y[interfaces.index(interface)]]
    m_filtered = [valor for valor in m if not np.isnan(valor)]
    x_filtered = list(range(1, len(m_filtered) + 1))
    plot_graph(x_filtered, m_filtered, nome, color)

# Add vertical lines
plt.axvline(x=30, color='gray', linestyle='--', linewidth=2)
plt.axvline(x=60, color='gray', linestyle='--', linewidth=2)
plt.axvline(x=90, color='gray', linestyle='--', linewidth=2)

# Final plot settings
plt.xlabel('Time (s)')
plt.ylabel('Throughput (Mbps)')
plt.title(f'Comparison of Traffic Splitting Methods for Elephant and Mice Flows')
plt.xlim(0, 400)  # Set x-axis limit from 0 to 1500
plt.tight_layout()

# Ajuste da legenda para ficar abaixo do gráfico
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fontsize=12, ncol=2)
plt.subplots_adjust(bottom=0.3, left=0.1, right=0.9, top=0.9)  # Ajuste conforme necessário

# Ajuste do tamanho da figura
fig = plt.gcf()
fig.set_size_inches(14, 7)  # Aumenta o tamanho da figura

# Save and clear plot
output_file_path = Path(f'result/fct_wcmp.png')
plt.savefig(output_file_path)
plt.clf()

print(f'{output_file_path}: OK')
