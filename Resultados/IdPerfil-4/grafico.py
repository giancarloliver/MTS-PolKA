import csv
import matplotlib.pyplot as plt

timestamps = []
throughputs = []

with open('s1-eth2.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Pula o cabeçalho

    for row in reader:
        if len(row) >= 3:
            try:
                timestamp = float(row[0])
                throughput_bytes = float(row[2])
                
                throughput_mbps = (throughput_bytes / (1024 * 1024)) * 8
                
                timestamps.append(timestamp)
                throughputs.append(throughput_mbps)
            except ValueError:
                pass

plt.plot(timestamps, throughputs)
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (Mbps)')
plt.title('Throughput vs Timestamp')
plt.show()
