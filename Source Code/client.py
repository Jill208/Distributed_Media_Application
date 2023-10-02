import socket
import os
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Define server's IP address and port
SERVER_HOST = '192.168.210.24'
SERVER_PORT = 8000

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Send the requested filename to the server
print("Enter filename you want to download: ")
requested_filename = input()
client_socket.send(requested_filename.encode())

# Receive the file size from the server
file_size_data = client_socket.recv(4096)
try:
    file_size_mb = float(file_size_data.decode())
except ValueError:
    error_message = file_size_data.decode()
    print(f"{Fore.RED}Error: {error_message}")
    client_socket.close()
    exit()

# Check if an error message was received
if "Error" in file_size_data.decode():
    error_message = file_size_data.decode()
    print(f"{Fore.RED}Error: {error_message}")
    client_socket.close()
    exit()

# Receive the file data from the server
file_data = b''
bytes_received = 0
chunk_size = 4096

print(f"{Fore.GREEN}Downloading {requested_filename} ({file_size_mb:.2f} MB):")
# Use tqdm to create a progress bar
with tqdm(total=file_size_mb, unit='MB', unit_scale=True, bar_format='{l_bar}{bar} {n_fmt}/{total_fmt}MB {elapsed} sec') as progress_bar:
    while bytes_received < file_size_mb * 1024 * 1024:
        # Receive a chunk of data from the server
        chunk = client_socket.recv(chunk_size)

        # If the chunk is empty, we have reached the end of the file
        if not chunk:
            break

        # Append the chunk to the file data
        file_data += chunk

        # Update the bytes received
        bytes_received += len(chunk)

        # Update the progress bar
        progress_bar.update(len(chunk) / (1024 * 1024))

# Save the file data to a file
with open(requested_filename, 'wb') as file:
    file.write(file_data)

print(f"{Fore.GREEN}\nDownloaded successfully: {requested_filename}")
print(f"File saved as: {requested_filename}")

# Close the socket
client_socket.close()
