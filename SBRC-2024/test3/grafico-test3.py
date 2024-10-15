import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path  # Add this line

run = 1
test = 1
taxa = 10

#interfaces = ['s1_0-eth3', 's1_0-eth4', 's2_1-eth2', 's2_2-eth3', 's1_1-eth1', 's1_1-eth2']

#interfaces = ['s1_0-eth2', 's1_0-eth3', 's1_0-eth4', 's1_0-eth5', 's1_0-eth6', 's1_1-eth1', 's1_1-eth3']

#interfaces = ['s1_0-eth2', 's1_0-eth3', 's1_0-eth4','s1_1-eth1']

#interfaces = ['s1_0-eth2', 's1_0-eth3', 's1_0-eth4', 's1_0-eth5', 's1_0-eth6', 's2_2-eth3', 's1_1-eth1', 's1_1-eth2', 's1_1-eth3']

#interfaces = ['s1_0-eth2', 's1_0-eth3', 's1_0-eth4', 's1_0-eth5', 's1_0-eth6', 's2_0-eth2', 's2_1-eth2', 's2_2-eth3', 's2_3-eth2', 's2_4-eth2', 's1_1-eth1', 's1_1-eth2', 's1_1-eth3']

interfaces = ['s1_0-eth1', 's1_1-eth1', 's1_1-eth2', 's1_1-eth3']
labels = ['H1 (origem tcp1 e tcp2)', 'H2 (destino tcp1)', 'H4 (destino udp1)', 'H5 (destino tcp2)']

plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)


def plot_graph(x, m, interface, color):
    #plt.plot(x, m, linewidth=1, color=color, label=interface)
    plt.plot(x, m, linewidth=1, marker='o', markersize=2, color=color, label=interface)

all_x = []
y = [[] for _ in range(len(interfaces))]

# Iterating over interfaces
for interface in interfaces:
    x = []
    for sample in range(1, 31):
        ignorar = 1
        maxplot = 208
        arq = f"data/run/{interface}-a{sample}.csv"
        print(f"Processing file: {arq}")  # Add this line for debugging
        try:
            with open(arq, 'r') as f:
                dados_arq = f.readlines()
                cont = 1
                ignore_zeros = True
                linhas = []
                for dado in dados_arq:
                    if ignorar > 0:
                        ignorar = ignorar -1
                    else:
                        if cont <= maxplot:
                            linhas.append(dado)
                    cont = cont + 1

                cont = 1
                for dado in linhas:
                    x.append((cont) /10)
                    # x.append((cont - 1) * 10)
                    y[interfaces.index(interface)].append([])
                    if interface == 's1_0-eth1':
                        b = dado.split(',')[3]
                    else:
                        b = dado.split(',')[2]
                    fb = float(b) / 1024 / 1024 * 8
                    y[interfaces.index(interface)][cont - 1].append(fb)
                    cont += 1
        except FileNotFoundError:
            print(f"File not found: {arq}")

     # Update x with accumulated values
    all_x.extend(x)

# Plotting the graphs
cores = ['green', 'red', 'orange', 'blue']


# Inside the loop where you plot interfaces
for interface, color, nome in zip(interfaces, cores, labels):
    m = [np.mean(dados) if dados else np.nan for dados in y[interfaces.index(interface)]]
    m_mbps = [valor / 1e6 for valor in m]

    # Create boolean mask for non-NaN values
    non_nan_indices = [i for i in range(len(m)) if not np.isnan(m[i])]

    # Filter x and m arrays using the boolean mask
    x_filtered = [x[i] for i in non_nan_indices]
    m_filtered = [m[i] for i in non_nan_indices]

    # Plot the graph using the function
    plot_graph(x_filtered, m_filtered, nome, color)


# Vertical lines at seconds 10, 20, and 30
plt.axvline(x=10, color='gray', linestyle='--', linewidth=2)
plt.axvline(x=20, color='gray', linestyle='--', linewidth=2)

# Final plot configurations
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (Mbps)')
plt.title(f'Múltiplos fluxos concorrentes e migração de perfil')
plt.tight_layout()

# Adding legend to the right of the plot
plt.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=15)

# Adjust the layout to increase the space for the legend
plt.subplots_adjust(right=0.75)  # Adjust the value as needed

fig = plt.gcf()
fig.set_size_inches(12, 6)  # You can adjust the size as needed

output_file_path = Path(f'result/test{test}.png')
plt.savefig(output_file_path)
plt.clf()

print(f'{output_file_path}: OK')