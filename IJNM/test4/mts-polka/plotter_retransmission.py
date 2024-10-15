import os
import re
import matplotlib.pyplot as plt

def extract_retransmissions(file_path):
    """
    Extract the number of retransmissions from an iperf3 output file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Find the line that contains the retransmissions in the summary
            match = re.search(r'\[ *\d+ *\] *\d+\.\d+-\d+\.\d+ *sec *[\d\.]+ *[MGK]Bytes *[\d\.]+ *[MGK]bits/sec *(\d+) *sender', content)
            if match:
                return int(match.group(1))
            else:
                return None
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None

# Directory containing the test output files
output_dir = 'retransmission/data/run'

# Define protocols and labels
protocolos = ['ecmp', 'wcmp', 'rps', 'mts-polka']
labels = ['ECMP', 'WCMP', 'RPS','MTS-PolKA']

# Collect retransmission counts for each protocol
retransmissions_per_protocol = {protocol: [] for protocol in protocolos}

# Process each protocol and extract retransmission counts
for protocol in protocolos:
    for i in range(1, 2):  # Adjust the range if you have more files
        file_path = os.path.join(output_dir, f'{protocol}.txt')
        retransmission_count = extract_retransmissions(file_path)
        if retransmission_count is not None:
            retransmissions_per_protocol[protocol].append(retransmission_count)
        else:
            print(f"Warning: No retransmission data found in {file_path}")

# Debug: Print the collected retransmission counts
print("Retransmissions per protocol:", retransmissions_per_protocol)

# Plotting the retransmissions for each protocol as a bar chart
plt.figure(figsize=(10, 6))

# Prepare data for bar chart
test_numbers = range(len(protocolos))
values = [retransmissions_per_protocol[protocol][0] for protocol in protocolos]  # Assuming one value per protocol

# Create bar chart
plt.bar(test_numbers, values, color=['blue', 'red', 'orange', 'green', 'grey' ], tick_label=labels)

# Annotate the bars with the values
for i, value in enumerate(values):
    plt.text(i, value + 200, str(value), ha='center', fontsize=8, color='black')

# Setting y-axis limits and ticks
plt.ylim(0, max(values) + 1000)  # Adjust y-axis limits
plt.yticks([x * 1000 for x in range((max(values) // 1000) + 2)])  # Adjust ticks to match the data range

plt.xlabel('Method')
plt.ylabel('Retransmissions')
# plt.title('Retransmissions for Each Protocol')
plt.grid(axis='y')

# Save plot to the new directory
output_image_path = os.path.join('retransmission', 'result', 'retransmissions_tcp.pdf')
plt.savefig(output_image_path)
plt.show()
