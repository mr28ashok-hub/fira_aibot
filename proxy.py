import socket
import sys
import struct
import threading

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data: break
            dst.sendall(data)
    except:
        pass

def main():
    proxy_host = "127.0.0.1"
    proxy_port = 1080
    target_host = sys.argv[1]
    target_port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((proxy_host, proxy_port))

    # SOCKS5 Auth
    s.sendall(b"\x05\x01\x00")
    resp = s.recv(2)

    # SOCKS5 Connect
    try:
        target_addr = socket.gethostbyname(target_host)
        host_bytes = socket.inet_aton(target_addr)
    except:
        # If hostname resolution fails, use domain name
        host_bytes = b"\x03" + len(target_host).to_bytes(1, 'big') + target_host.encode()

    port_bytes = struct.pack(">H", target_port)
    s.sendall(b"\x05\x01\x00\x01" + host_bytes + port_bytes)
    resp = s.recv(10)

    if resp[1] != 0:
        sys.stderr.write(f"SOCKS5 error: {resp[1]}\n")
        sys.exit(1)

    t = threading.Thread(target=pipe, args=(s, sys.stdout.buffer))
    t.daemon = True
    t.start()

    while True:
        data = sys.stdin.buffer.read(4096)
        if not data: break
        s.sendall(data)

if __name__ == "__main__":
    main()
