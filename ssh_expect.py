import sys
import pty
import os
import subprocess
import time

def main():
    host = "oofqu-2402-1980-c2e-b22b--1bb.run.pinggy-free.link"
    port = "40247"
    user = "pi"
    password = "turtlebot"

    # Command to retrieve map.yaml, room_locations.yaml, and base64 encoded map.pgm
    remote_cmd = (
        "echo '---BEGIN map.yaml---' && cat ~/map.yaml && echo '---END map.yaml---' && "
        "echo '---BEGIN room_locations.yaml---' && cat ~/catkin_ws/src/tb3_8gb/config/room_locations.yaml && echo '---END room_locations.yaml---' && "
        "echo '---BEGIN map.pgm.b64---' && base64 ~/map.pgm && echo '---END map.pgm.b64---'"
    )

    ssh_cmd = ["ssh", "-p", port, "-o", "StrictHostKeyChecking=no", f"{user}@{host}", remote_cmd]

    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(ssh_cmd[0], ssh_cmd)
    else:
        buffer = b""
        start_time = time.time()
        # Binary data might take longer to transfer
        while time.time() - start_time < 120:
            try:
                data = os.read(fd, 8192)
                if not data:
                    break
                buffer += data
                output = data.decode(errors='ignore')
                # Printing might be slow for large binary buffers, so we'll be careful
                if "password:" in output.lower():
                    os.write(fd, f"{password}\n".encode())
            except OSError:
                break

        # Save the full raw buffer for extraction
        with open("raw_backup_data.txt", "wb") as f:
            f.write(buffer)

if __name__ == "__main__":
    main()
