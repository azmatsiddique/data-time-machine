
import os
import pty
import sys
import struct
import fcntl
import termios
import subprocess
import time

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

def main():
    # Desired dimensions
    cols = 120
    rows = 40
    
    print(f"Starting recording with forced dimensions: {cols}x{rows}")
    
    # Command to run: asciinema record -> python visual_demo.py
    # We wrap this in a pty to control dimensions
    
    # We want to run: asciinema rec demo/demo.cast --overwrite -c "python3 scripts/visual_demo.py"
    cmd = [
        "asciinema", "rec", "demo/demo.cast", 
        "--overwrite", 
        "-c", "python3 scripts/visual_demo.py"
    ]
    
    pid, fd = pty.fork()
    
    if pid == 0:
        # Child process
        # No need to set winsize here, the master sets it on the slave end generally, 
        # but pty.fork sets the controlling terminal.
        # Let's just execute the command.
        os.execvp(cmd[0], cmd)
    else:
        # Parent process
        # Set window size of the pty
        set_winsize(fd, rows, cols)
        
        try:
            # COPY stdin to pty, and pty output to stdout
            # This is a simple loop. 
            # In a real robust implementation we'd use select, but 
            # visual_demo.py is non-interactive (automated).
            # So we mainly need to read from fd and print to stdout.
            
            while True:
                try:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                except OSError:
                    break
        except KeyboardInterrupt:
            pass
        
        os.waitpid(pid, 0)
        print("\nRecording finished.")

if __name__ == "__main__":
    main()
