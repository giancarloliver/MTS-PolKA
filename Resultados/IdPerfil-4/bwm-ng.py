import os
import time

interfaces = [
    "s1-eth2",
    "s1-eth4",
    "s1-eth6",
    "s2-eth2",
    "s4-eth2",
    "s6-eth2",
    "s7-eth1"
]

duration = 1000  # Tempo em milissegundos

# Defina a duração do teste (em segundos)
test_duration = 64

# Calcule o número de iterações com base na duração total do teste e a duração de cada teste individual
num_iterations = int((test_duration * 1000) / duration)

for _ in range(num_iterations):
    for interface in interfaces:
        command = f"bwm-ng -t {duration} -I {interface} -o csv -u bytes -T rate -C ',' > {interface}.csv &"
        os.system(command)
    time.sleep(duration / 1000)  # Espera a duração de cada teste antes de iniciar o próximo

# Aguarda o término do último teste antes de finalizar o script
time.sleep(duration / 1000)

