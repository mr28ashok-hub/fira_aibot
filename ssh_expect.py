import sys
import pty
import os
import subprocess
import time

def main():
    host = "bmhmk-2402-1980-c2e-b22b--1bb.run.pinggy-free.link"
    port = "35743"
    user = "pi"
    password = "turtlebot"

    # Read the files
    remote_cmd = (
        "echo '---BEGIN map.yaml---' && cat ~/map.yaml && echo '---END map.yaml---' && "
        "echo '---BEGIN room_locations.yaml---' && cat ~/catkin_ws/src/tb3_8gb/config/room_locations.yaml && echo '---END room_locations.yaml---'"
    )

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
