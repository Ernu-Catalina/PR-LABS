import socket
import ssl


def send_https_request(host, path):
    context = ssl.create_default_context()
    sock = socket.create_connection((host, 443))
    secure_sock = context.wrap_socket(sock, server_hostname=host)

    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    secure_sock.sendall(request.encode())

    response = b""
    while True:
        data = secure_sock.recv(4096)
        if not data:
            break
        response += data

    secure_sock.close()

    response_str = response.decode()

    headers, body = response_str.split("\r\n\r\n", 1)

    return body


host = 'educationalcentre.md'
path = '/shop/index.php?route=product/category&path=2350_2355_2361'

html_content = send_https_request(host, path)

print(html_content)
