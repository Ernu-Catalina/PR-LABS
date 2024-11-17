import socket
import threading
import random
import time
import os

FILE_NAME = 'shared_file.txt'

file_lock = threading.Lock()


def handle_client(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(f"Received message: {message}")

            sleep_time = random.randint(1, 7)
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

            if message.startswith("WRITE"):
                data = message[len("WRITE "):].strip()
                write_to_file(data)
                client_socket.send(f"Data '{data}' written to the file.".encode())
            elif message == "READ":
                content = read_from_file()
                client_socket.send(content.encode())
            else:
                client_socket.send("Invalid command. Use 'WRITE <data>' or 'READ'.".encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


def read_from_file():
    with file_lock:
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'r') as file:
                return file.read()
        else:
            return "File does not exist."


def write_to_file(data):
    with file_lock:
        with open(FILE_NAME, 'a') as file:
            file.write(data + '\n')


def start_server(host='localhost', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}...")

    try:
        while True:
            client_socket, client_address = server.accept()
            print(f"Accepted connection from {client_address}")

            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
