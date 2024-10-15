import os
import re
import matplotlib.pyplot as plt

def extract_retransmissions(file_path):
    """
    Extract the number of retransmissions from an iperf3 output file.
    """
    with open(file_path, 'r') as file:
        content = file.read()
        # Find the line that contains the retransmissions in the summary
        match = re.search(r'\[ *\d+ *\] *\d+\.\d+-\d+\.\d+ *sec *[\d\.]+ *[MGK]Bytes *[\d\.]+ *[MGK]bits/sec *(\d+) *sender', content)
        if match:
            return int(match.group(1))
        else:
            return None

# Directory containing the test output files
output_dir = 'data/run'

# Collect retransmission counts from all test files
retransmissions = []

for i in range(1, 31):
    file_path = os.path.join(output_dir, f'output-P0-10M_{i}.txt')
    retransmission_count = extract_retransmissions(file_path)
    if retransmission_count is not None:
        retransmissions.append(retransmission_count)
    else:
        print(f"Warning: No retransmission data found in {file_path}")

# Calculate the average retransmissions
if retransmissions:
    average_retransmissions = sum(retransmissions) / len(retransmissions)
    print(f"Average Retransmissions: {average_retransmissions:.2f}")

    # Plotting the retransmissions
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 31), retransmissions, marker='o', linestyle='-', color='b', label='Retransmissions')
    plt.axhline(y=average_retransmissions, color='r', linestyle='--', label=f'Average: {average_retransmissions:.2f}')
    plt.xlabel('Test Number')
    plt.ylabel('Retransmissions')
    plt.title('Retransmissions per Test with Average')
    plt.legend()
    plt.grid(True)
    plt.savefig('data/run/retransmissions_plot.png')
    plt.show()
else:
    print("No retransmission data found in any files.")
