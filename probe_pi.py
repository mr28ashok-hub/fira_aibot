import socket
import struct
import sys

def check_port(proxy_host, proxy_port, target_host, target_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((proxy_host, proxy_port))

        # SOCKS5 Auth
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if resp != b"\x05\x00":
            return f"Auth failed: {resp.hex()}"

        # SOCKS5 Connect
        target_addr = socket.gethostbyname(target_host)
        host_bytes = socket.inet_aton(target_addr)
        port_bytes = struct.pack(">H", target_port)
        s.sendall(b"\x05\x01\x00\x01" + host_bytes + port_bytes)
        resp = s.recv(10)

        if resp[1] == 0:
            return "OPEN"
        else:
            return f"CLOSED (code {resp[1]})"
    except Exception as e:
        return f"ERROR: {e}"

proxy = "127.0.0.1"
port = 1080
target = "10.105.194.82"

print(f"Port 80: {check_port(proxy, port, target, 80)}")
print(f"Port 22: {check_port(proxy, port, target, 22)}")
