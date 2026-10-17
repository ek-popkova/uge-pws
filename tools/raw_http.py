"""HTTP with no library at all: open a socket, type the request, read the answer."""

import socket

HOST, PORT = "127.0.0.1", 8000

request = (
    "GET /products/42 HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    "Accept: application/json\r\n"
    "Connection: close\r\n"
    "\r\n"
)

with socket.create_connection((HOST, PORT), timeout=5) as sock:
    sock.sendall(request.encode("ascii"))
    answer = b""
    while chunk := sock.recv(4096):
        answer += chunk

print(answer.decode("utf-8", "replace"))
