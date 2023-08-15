import matplotlib.pyplot as plt
import numpy as np
import glob
import csv

# Function to read data from CSV files
def read_csv_files(file_names):
    data = {}

    for i, file_name in enumerate(file_names):
        print(file_name)

        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            for row in reader:
                if len(row) >= 3:
                    timestamp, iface_name, bytes_out_s = row[:3]
                    try:
                        timestamp = float(timestamp)
                        throughput_mbps = float(bytes_out_s) * 8 / 1024 / 1024
                        if timestamp not in data:
                            data[timestamp] = [np.nan] * len(file_names)
                        data[timestamp][i] = throughput_mbps
                    except (ValueError, TypeError):
                        continue

    # Convert data dictionary to x and y arrays
    x = []
    y = [[] for _ in file_names]

    for timestamp, values in sorted(data.items()):
        x.append(timestamp)
        for i, value in enumerate(values):
            y[i].append(value)

    return x, y

# Configuration
run = 1

# Matplotlib settings
plt.rc('font', size=16)
plt.rc('axes', titlesize=16)
plt.rc('axes', labelsize=16)
plt.rc('xtick', labelsize=16)
plt.rc('ytick', labelsize=16)
plt.rc('legend', fontsize=10)
plt.rc('figure', titlesize=16)

# Read all CSV files in the current directory
csv_files = glob.glob('*.csv')

# Read data from CSV files
x, y = read_csv_files(csv_files)

# Calculate the mean values for each file
means = [np.nanmean(data) for data in y]

# Plotting
for i, file_name in enumerate(csv_files):
    plt.plot(x, y[i], linewidth=2, marker='o', markersize=3, label=f'File {i+1}: {file_name}')

plt.xlabel('Time (s)')
plt.ylabel('Throughput (Mbps)')
plt.title('Switch Throughput over Time')
plt.legend(loc='upper right')
plt.show()
