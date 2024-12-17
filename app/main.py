import socket  # noqa: F401
from sqlite3 import connect


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept() # wait for client
    get_request = client_socket.recv(1024).decode().split()
    if get_request[1] == "/":
        client_socket.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
    elif "/echo/" in get_request[1]:
        echo_str = get_request[1][6:]
        client_socket.sendall(f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_str)}\r\n\r\n{echo_str}'.encode())
    else:
        client_socket.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')

if __name__ == "__main__":
    main()
