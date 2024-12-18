import socket  # noqa: F401
from sqlite3 import connect
import threading

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client_socket, client_address = server_socket.accept()  # wait for client
        threading.Thread(target=send_successful_connection_message, args=(client_socket,)).start()

def send_successful_connection_message(client_socket):
    get_request = client_socket.recv(1024).decode().split()

    if get_request[1] == "/":
        client_socket.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
    elif "/echo/" in get_request[1]:
        echo_str = get_request[1][6:]
        client_socket.sendall(
            f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_str)}\r\n\r\n{echo_str}'.encode())
    elif get_request[1] == "/user-agent" and get_request[-2] == "User-Agent:":
        client_socket.sendall(
            f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(get_request[-1])}\r\n\r\n{get_request[-1]}'.encode())
    else:
        client_socket.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')


if __name__ == "__main__":
    main()
