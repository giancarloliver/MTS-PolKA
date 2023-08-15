import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('iperf_output.csv', parse_dates=['Time'])

# Extract the relevant columns
timestamps = [datetime.strptime(ts, '%Y%m%d%H%M%S') for ts in df['Time']]
throughput = df['Transfer']

# Create the line plot
plt.plot(timestamps, throughput)
plt.xlabel('Time')
plt.ylabel('Throughput (bits/s)')
plt.title('Throughput over Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
