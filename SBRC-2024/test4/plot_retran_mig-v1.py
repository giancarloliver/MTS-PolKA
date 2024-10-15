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
output_dir = 'data/test4/run2'

# Profiles to process and number of files per profile
profiles = [0, 3]
files_per_profile = 30

# Colors for the average lines
average_colors = {0: 'green', 3: 'red'}

# Collect retransmission counts for each profile
retransmissions_per_profile = {profile: [] for profile in profiles}

for profile in profiles:
    for i in range(1, files_per_profile + 1):
        file_path = os.path.join(output_dir, f'output_perfil{profile}_{i}.txt')
        retransmission_count = extract_retransmissions(file_path)
        if retransmission_count is not None:
            retransmissions_per_profile[profile].append(retransmission_count)
        else:
            print(f"Warning: No retransmission data found in {file_path}")

# Plotting the retransmissions for each profile
plt.figure(figsize=(10, 6))

for profile in profiles:
    if retransmissions_per_profile[profile]:
        average_retransmissions = sum(retransmissions_per_profile[profile]) / len(retransmissions_per_profile[profile])
        plt.plot(range(1, files_per_profile + 1), retransmissions_per_profile[profile], marker='o', linestyle='-', label=f'Perfil {profile}')
        plt.axhline(y=average_retransmissions, linestyle='--', color=average_colors[profile], label=f'Média Perfil {profile}: {average_retransmissions:.2f}')
    else:
        print(f"No retransmission data found for profile {profile}")

# Setting y-axis limits and ticks
plt.ylim(-0.5, 5)
plt.yticks([x * 0.5 for x in range(11)])

plt.xlabel('Número do Teste')
plt.ylabel('Retransmissões')
plt.title('Retransmissões por Teste para cada Perfil')
plt.legend()
plt.grid(True)
plt.savefig('data/test4/run2/retransmissions_perfil.png')
plt.show()
