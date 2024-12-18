import os
import socket  # noqa: F401
from sqlite3 import connect
import threading
import sys
import gzip

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client_socket, client_address = server_socket.accept()  # wait for client
        threading.Thread(target=handle_request, args=(client_socket,)).start()

def handle_request(client_socket):
    get_request = client_socket.recv(1024).decode().split()
    print(get_request)
    if get_request[1] == "/":
        client_socket.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
    elif get_request[1].startswith("/echo/"):
        echo_str = get_request[1][6:]
        if "gzip," in get_request or 'gzip' in get_request:
            echo_str = gzip.decompress(echo_str)
            client_socket.sendall(f'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_str)}\r\n\r\n{echo_str}'.encode())
        else:
            client_socket.sendall(f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_str)}\r\n\r\n{echo_str}'.encode())
    elif get_request[1] == "/user-agent" and get_request[-2] == "User-Agent:":
        client_socket.sendall(f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(get_request[-1])}\r\n\r\n{get_request[-1]}'.encode())
    elif get_request[1].startswith('/files/') and sys.argv[-2] == '--directory' and os.path.isfile(sys.argv[2] + get_request[1][7:]):
        with open(sys.argv[2] + get_request[1][7:], 'r') as f:
            contents = f.read()
        client_socket.sendall(f'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(contents)}\r\n\r\n{contents}'.encode())
    elif get_request[0] == "POST" and get_request[1].startswith("/files/"):
        path = sys.argv[2] + get_request[1][7:]
        with open(path, 'w') as f:
            f.write(' '.join(get_request[get_request.index('application/octet-stream') + 1:]))
        client_socket.sendall(b'HTTP/1.1 201 Created\r\n\r\n')
    else:
        client_socket.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')


if __name__ == "__main__":
    main()
