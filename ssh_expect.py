import sys
import pty
import os
import subprocess
import time

def main():
    # Placeholder connection details. Update these with fresh values from Pinggy.
    host = "PLACEHOLDER_HOST"
    port = "PLACEHOLDER_PORT"
    user = "pi"
    password = "PLACEHOLDER_PASSWORD"

    # Example command
    remote_cmd = "grep 'alias cm=' ~/.bashrc"

    ssh_cmd = ["ssh", "-p", port, "-o", "StrictHostKeyChecking=no", f"{user}@{host}", remote_cmd]

    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(ssh_cmd[0], ssh_cmd)
    else:
        buffer = b""
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                buffer += data
                output = data.decode(errors='ignore')
                print(output, end='', flush=True)
                if "password:" in output.lower():
                    os.write(fd, f"{password}\n".encode())
            except OSError:
                break
        time.sleep(2)

if __name__ == "__main__":
    main()
