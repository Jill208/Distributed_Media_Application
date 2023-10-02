import socket
import threading
import os
import queue

# Define server's IP address and port
SERVER_HOST = '192.168.210.24'
SERVER_PORT = 8000

# Define the directory where the multimedia files are stored
MEDIA_DIR = 'C:/Users/jillc/Desktop/DAIICT Lecture notes/Sem-6/Distributed System/Project/Video'

# Define the maximum file size (in bytes) that the server can transfer
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server address to the socket
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

# Create a queue to store client requests
request_queue = queue.Queue()

def handle_client(client_socket, client_addr):
    # Receive the requested filename from the client
    requested_filename = client_socket.recv(1024).decode()

    # Construct the file path
    file_path = os.path.join(MEDIA_DIR, requested_filename)

    try:
        # Check if the file exists
        if os.path.isfile(file_path):
            # Get the file size
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            # Send the file size to the client
            client_socket.send(str(file_size_mb).encode())

            # Open the file in binary mode
            with open(file_path, 'rb') as file:
                # Read and send the file data in chunks
                chunk_size = 4096
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    client_socket.send(chunk)
            
            print(f"[*] Sent {requested_filename} ({file_size} bytes) to {client_addr[0]}:{client_addr[1]}")
        else:
            # If the file doesn't exist, send an error message to the client
            error_message = f"Error: File '{requested_filename}' not found"
            client_socket.sendall(error_message.encode())

    except Exception as e:
        # Send an error message to the client
        error_message = f"Error: {str(e)}"
        client_socket.sendall(error_message.encode())

    finally:
        # Close the client socket
        client_socket.close()

while True:
    # Accept a client connection
    client_socket, client_addr = server_socket.accept()
    print(f"[*] Accepted connection from {client_addr[0]}:{client_addr[1]}")

    # Add the client request to the queue
    request_queue.put((client_socket, client_addr))

    # If there are requests in the queue, start processing them
    while not request_queue.empty():
        client_socket, client_addr = request_queue.get()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.start()
