import os
import socket
import threading
import sys
import gzip

HTTP_200_OK = "HTTP/1.1 200 OK\r\n"
HTTP_201_CREATED = "HTTP/1.1 201 Created\r\n"
HTTP_404_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"

def send_response(client_socket, headers, body=b""):
    response = headers.encode() + b"\r\n" + body
    client_socket.sendall(response)

def handle_root(client_socket):
    send_response(client_socket, HTTP_200_OK)

def handle_echo(client_socket, request_path, accept_gzip):
    echo_str = request_path[6:]
    print(echo_str)
    if accept_gzip:
        echo_str = gzip.compress(echo_str.encode())
        headers = (
            f"{HTTP_200_OK}Content-Encoding: gzip\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(echo_str)}\r\n"
        )
        send_response(client_socket, headers, echo_str)
    else:
        headers = (f"{HTTP_200_OK}Content-Type: text/plain\r\n"
                   f"Content-length: {len(echo_str)}\r\n"
        )
        send_response(client_socket, headers, echo_str.encode())

def handle_user_agent(client_socket, headers):
    user_agent = headers.get("User-Agent", "Unknown")
    response_body = user_agent.encode()
    headers = (
        f"{HTTP_200_OK}Content-Type: text/plain\r\n"
        f"Content-Length: {len(response_body)}\r\n"
    )
    send_response(client_socket, headers, response_body)

def handle_file_request(client_socket, request_path):
    try:
        with open(sys.argv[2] + request_path[7:], 'rb') as f:
            response_body = f.read()
        headers = (
            f"{HTTP_200_OK}Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(response_body)}\r\n"
        )
        send_response(client_socket, headers, response_body)
    except FileNotFoundError:
        send_response(client_socket, HTTP_404_NOT_FOUND)

def handle_file_upload(client_socket, request_path, request_body):
    with open(sys.argv[2] + request_path[7:], 'wb') as f:
        f.write(request_body)
    send_response(client_socket, HTTP_201_CREATED)

def parse_and_process_request(client_socket):
    request = client_socket.recv(1024).decode()
    request_line, *header_lines = request.split("\r\n")
    method, path, _ = request_line.split()
    headers = {
        key: value.strip() for line in header_lines if (key := line.split(":")[0]) and (value := line.split(":", 1)[-1])
    }
    body = request.split("\r\n\r\n", 1)[-1].encode() if "\r\n\r\n" in request else b""

    accept_gzip = "gzip" in headers.get("Accept-Encoding", "")

    if path == "/":
        handle_root(client_socket)
    elif path.startswith("/echo/"):
        handle_echo(client_socket, path, accept_gzip)
    elif path == "/user-agent":
        handle_user_agent(client_socket, headers)
    elif path.startswith("/files/") and method == "GET":
        handle_file_request(client_socket, path)
    elif path.startswith("/files/") and method == "POST":
        handle_file_upload(client_socket, path, body)
    else:
        send_response(client_socket, HTTP_404_NOT_FOUND)

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=parse_and_process_request, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
