import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

run = 1
test = 1
taxa = 10

# Define interfaces and labels
interfaces = ['s1_1-eth1', 's1_1-eth3']
labels = ['H2 (destino tcp1)', 'H5 (destino tcp2)']

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
for interface in interfaces:
    x = []
    for sample in range(1, 11):
        ignorar = 1
        maxplot = 208
        arq = f"data/run/{interface}-a{sample}.csv"
        print(f"Processing file: {arq}")  # Debugging line
        try:
            with open(arq, 'r') as f:
                dados_arq = f.readlines()
                cont = 1
                ignore_zeros = True
                linhas = []
                for dado in dados_arq:
                    if ignorar > 0:
                        ignorar -= 1
                    else:
                        if cont <= maxplot:
                            linhas.append(dado)
                    cont += 1

                cont = 1
                for dado in linhas:
                    x.append(cont)  # Use actual sample index for x
                    y[interfaces.index(interface)].append([])
                    b = dado.split(',')[3] if interface == 's1_0-eth1' else dado.split(',')[2]
                    fb = float(b) / 1024 / 1024 * 8
                    y[interfaces.index(interface)][cont - 1].append(fb)
                    cont += 1
        except FileNotFoundError:
            print(f"File not found: {arq}")

    all_x.extend(x)

# Plotting
cores = ['green', 'red', 'orange']
for interface, color, nome in zip(interfaces, cores, labels):
    m = [np.mean(dados) if dados else np.nan for dados in y[interfaces.index(interface)]]
    m_mbps = [valor / 1e6 for valor in m]
    non_nan_indices = [i for i in range(len(m)) if not np.isnan(m[i])]
    x_filtered = [x[i] for i in non_nan_indices]
    m_filtered = [m[i] for i in non_nan_indices]
    plot_graph(x_filtered, m_filtered, nome, color)

# Add vertical lines
plt.axvline(x=10, color='gray', linestyle='--', linewidth=2)
plt.axvline(x=20, color='gray', linestyle='--', linewidth=2)
plt.axvline(x=30, color='gray', linestyle='--', linewidth=2)

# Final plot settings
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (Mbps)')
plt.title(f'Múltiplos fluxos concorrentes e migração de perfil')
plt.xlim(0, 120)  # Set x-axis limit from 0 to 110
plt.tight_layout()

# Legend and layout adjustment
plt.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=15)
plt.subplots_adjust(right=0.75)  # Adjust as needed
fig = plt.gcf()
fig.set_size_inches(12, 6)

# Save and clear plot
output_file_path = Path(f'result/test{test}.png')
plt.savefig(output_file_path)
plt.clf()

print(f'{output_file_path}: OK')
