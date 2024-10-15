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

def process_files(output_dir, profile_name):
    retransmissions = []

    for i in range(1, 31):
        file_path = os.path.join(output_dir, f'output_{profile_name}_{i}.txt')
        retransmission_count = extract_retransmissions(file_path)
        if retransmission_count is not None:
            retransmissions.append(retransmission_count)
        else:
            print(f"Warning: No retransmission data found in {file_path}")

    if retransmissions:
        average_retransmissions = sum(retransmissions) / len(retransmissions)
        deviation = [count - average_retransmissions for count in retransmissions]
        return average_retransmissions, deviation
    else:
        return None, None

# Directory containing the test output files
output_dir = 'data/test4/run2'

# Process data for profile 0
avg_retrans_profile0, deviation_profile0 = process_files(output_dir, 'perfil0')

# Process data for profile 3
avg_retrans_profile3, deviation_profile3 = process_files(output_dir, 'perfil3')

# Plotting
if avg_retrans_profile0 is not None and avg_retrans_profile3 is not None:
    plt.figure(figsize=(10, 6))
    
    # Time points
    time_points = [0, 10, 20]
    
    # Plot profile 0 data
    plt.errorbar(time_points, [avg_retrans_profile0] * len(time_points), yerr=[0, 0, 0], fmt='o', linestyle='-', color='b', label='Perfil 0')
    
    # Plot profile 3 data
    plt.errorbar(time_points, [avg_retrans_profile3] * len(time_points), yerr=[0, 0, 0], fmt='o', linestyle='-', color='r', label='Perfil 3')
    
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Desvio de Retransmissão')
    plt.title('Média de Retransmissão com Desvio ao Longo do Tempo')
    plt.xticks(time_points)
    plt.legend()
    plt.grid(True)
    plt.savefig('data/test4/run2/retransmissoes_perfil0_perfil3.png')
    plt.show()
else:
    print("Nenhum dado de retransmissão encontrado nos arquivos.")
