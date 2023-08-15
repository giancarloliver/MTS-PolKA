import sys
import time

def extract_send_times(file_path):
    with open(file_path, 'r') as send_file:
        send_times = [float(line.strip()) for line in send_file]
    return send_times

def calculate_throughput(packet_count, start_time, end_time):
    duration = end_time - start_time
    throughput = packet_count / duration
    return throughput

def main():
    if len(sys.argv) != 2:
        print("Usage: python receive.py send_times.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    send_times = extract_send_times(file_path)

    packet_count = len(send_times)
    if packet_count == 0:
        print("No packets received.")
        sys.exit(0)

    start_time = send_times[0]
    end_time = send_times[-1]

    # Calculate throughput per second
    throughput_per_second = {}
    for timestamp in send_times:
        second = int(timestamp)
        throughput_per_second[second] = throughput_per_second.get(second, 0) + 1

    total_throughput = calculate_throughput(packet_count, start_time, end_time)

    print(f"Total packets received: {packet_count}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Test duration: {end_time - start_time:.2f} seconds")
    print(f"Total throughput: {total_throughput:.2f} packets per second")
    print("\nThroughput per second:")
    for second, throughput in throughput_per_second.items():
        print(f"{second} seconds: {throughput} packets")

if __name__ == '__main__':
    main()
