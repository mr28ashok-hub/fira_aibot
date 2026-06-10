import sys
import pty
import os
import subprocess
import time

def main():
    # Use environment variables for sensitive info
    host = os.getenv("ROBOT_HOST", "PLACEHOLDER_HOST")
    port = os.getenv("ROBOT_PORT", "PLACEHOLDER_PORT")
    user = os.getenv("ROBOT_USER", "pi")
    password = os.getenv("ROBOT_PASSWORD", "PLACEHOLDER_PASSWORD")

    remote_cmd = sys.argv[1] if len(sys.argv) > 1 else "hostname"

    ssh_cmd = ["ssh", "-p", port, "-o", "StrictHostKeyChecking=no", f"{user}@{host}", remote_cmd]

    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(ssh_cmd[0], ssh_cmd)
    else:
        buffer = b""
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                data = os.read(fd, 4096)
                if not data:
                    break
                buffer += data
                output = data.decode(errors='ignore')
                print(output, end='', flush=True)
                if "password:" in buffer.decode(errors='ignore').lower():
                    os.write(fd, f"{password}\n".encode())
                    buffer = b"" # Clear buffer after sending password
            except OSError:
                break
        time.sleep(2)

if __name__ == "__main__":
    main()
