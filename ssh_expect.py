import sys
import pty
import os
import subprocess
import time

def main():
    cmd = ["ssh", "-p", "443", "-o", "StrictHostKeyChecking=no", "tfymq@a.pinggy.io"]

    # This is a very basic way to handle password input without pexpect
    # It might not work perfectly but it's worth a try
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd[0], cmd)
    else:
        # Read from fd and look for password prompt
        buffer = b""
        start_time = time.time()
        while time.time() - start_time < 20:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                buffer += data
                print(data.decode(errors='ignore'), end='', flush=True)
                if b"password:" in buffer.lower():
                    os.write(fd, b"turtlebot\n")
                    buffer = b"" # clear buffer to avoid re-triggering
                if b"Authenticated" in buffer or b"tfymq@" in buffer:
                     # Once authenticated, we might need to stay alive or run a command
                     pass
            except OSError:
                break

        # Keep it open for a bit to see output
        time.sleep(5)

if __name__ == "__main__":
    main()
