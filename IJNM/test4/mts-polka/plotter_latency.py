import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

method = 'mts-polka'

# Define protocolos and labels
paths = ['path1', 'path2', 'path3', 'path4', 'path5']
labels = ['PATH 1', 'PATH 2', 'PATH 3', 'PATH 4', 'PATH 5']

# Cores especificadas
colors = ['green', 'blue', 'red', 'orange', 'grey']

# Plot settings
plt.rc('font', size=18)
plt.rc('axes', titlesize=18)
plt.rc('axes', labelsize=18)
plt.rc('xtick', labelsize=18)
plt.rc('ytick', labelsize=18)
plt.rc('legend', fontsize=16)
plt.rc('figure', titlesize=18)

# Initialize a list to store the latency data for each protocol
y = [[] for _ in range(len(paths))]

# Process files and gather data
for path_idx, path in enumerate(paths):
    ignorar = 1
    arq = f"latency_test/data/run3/{method}_{path}.log"
    print(f"Processing file: {arq}")  # Debugging line
    try:
        with open(arq, 'r') as f:
            dados_arq = f.readlines()
            print(f"Total lines read: {len(dados_arq)}")  # Debugging line
            for cont, dado in enumerate(dados_arq, start=1):
                if ignorar > 0:
                    ignorar -= 1
                else:
                    if cont < 52:  # Assuming the first 52 lines are of interest
                        b = dado.split('=')[3]  # Coluna 4
                        fb = float(b.split(' ')[0])
                        # Append data to the corresponding protocol
                        y[path_idx].append(fb)
    except FileNotFoundError:
        print(f"File not found: {arq}")

    print(f"Data collected for {path}: {len(y[path_idx])} points")  # Debugging line

    # Visualize the distribution of the data
    plt.figure(figsize=(10, 5))
    plt.hist(y[path_idx], bins=30, alpha=0.7, color='blue')
    plt.xlabel('Latency (ms)')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of Latency for {labels[path_idx]}')
    plt.show()

    # Identify outliers
    q1 = np.percentile(y[path_idx], 25)
    q3 = np.percentile(y[path_idx], 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = [x for x in y[path_idx] if x < lower_bound or x > upper_bound]
    print(f'Outliers for {labels[path_idx]}: {outliers}')

# Calculate the mean and median of each protocol
means = [np.mean(data) for data in y]
medians = [np.median(data) for data in y]

# Plotting Boxplot
plt.figure(figsize=(14, 7))  # Adjust the size of the figure
box = plt.boxplot(y, patch_artist=True, labels=labels, showmeans=True)

# Customize boxplot colors
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

# Customize mean marker colors
for mean in box['means']:
    mean.set_color('black')  # Set mean marker color to black

# Customize whisker colors
for whisker, color in zip(box['whiskers'], [c for c in colors for _ in range(2)]):
    whisker.set_color(color)

# Customize cap colors
for cap, color in zip(box['caps'], [c for c in colors for _ in range(2)]):
    cap.set_color(color)

# Customize median colors
for median, color in zip(box['medians'], colors):
    median.set_color('black')  # Set median line color to black

# Add gridlines
plt.grid(True)

# Jitter settings and scatter plot of individual data points
for i in range(len(y)):
    jitter = np.random.normal(0, 0.04, size=len(y[i]))  # Adds a little noise horizontally
    plt.scatter(np.full(len(y[i]), i + 1) + jitter, y[i], alpha=0.6, color=colors[i], edgecolor='black', zorder=2)

# Adding the mean values to the legend
mean_labels = [f'{label} (mean = {mean:.2f} ms)' for label, mean in zip(labels, means)]

# Create custom legend with boxplot colors
from matplotlib.patches import Patch
legend_patches = [Patch(facecolor=color, edgecolor='black', label=mean_label) for color, mean_label in zip(colors, mean_labels)]

# Position the legend in the center at the top inside the plot
plt.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, 0.9), frameon=False)

# Increase the y-axis limit to 13,000
plt.ylim(0, 500)  # Ajuste o limite superior para 13000

# Labels without title
plt.xlabel(method)
plt.ylabel('Latency (ms)')

# Save and clear plot
output_file_path = Path(f'latency_test/result/latency_mts-polka3.pdf')
plt.savefig(output_file_path, bbox_inches='tight')  # bbox_inches='tight' to ensure full legend is saved
plt.clf()

print(f'{output_file_path}: OK')
