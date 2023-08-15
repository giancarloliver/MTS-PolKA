import subprocess
import multiprocessing

def execute_bwm_ng(interface):
    command = f"bwm-ng -t 1000 -I {interface} -o csv -u bytes -T rate -C ',' > {interface}.csv"
    print(f"Executing command: {command}")
    
    # Execute the command in a subprocess
    subprocess.run(command, shell=True)

def bwm_ng_interfaces(interfaces):
    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=len(interfaces))
    
    # Execute the bwm-ng command for each interface in parallel
    pool.map(execute_bwm_ng, interfaces)
    
    # Close the pool of worker processes
    pool.close()
    pool.join()

# Example usage
interfaces = ["s1-eth2", "s1-eth4", "s1-eth6", "s2-eth2", "s4-eth2", "s6-eth2", "s7-eth1"]
bwm_ng_interfaces(interfaces)
