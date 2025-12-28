
import sys
import time
import subprocess
import os
import shutil

# ANSI escape codes for colors
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def type_print(text, delay=0.05, end='\n'):
    """Simulate typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()

def run_step(prompt_text, command, simulate_typing=True):
    """Run a single step of the demo"""
    # Print prompt
    sys.stdout.write(f"{Colors.GREEN}user@dtm-demo{Colors.RESET}:{Colors.BLUE}~/data-project{Colors.RESET}$ ")
    
    if simulate_typing:
        type_print(command, delay=0.08)
    else:
        print(command)
        
    time.sleep(0.5)
    
    # Execute command
    # We need to run this in the actual shell to show real output
    # But for specialized demo logic we might handle some manually
    
    print(f"{Colors.RESET}", end='') # Reset before command output
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() # Ensure we can find src
    
    # Replace 'dtm' with the actual python execution for the demo
    real_command = command.replace("dtm", f"{sys.executable} -m src.cli")
    
    try:
        # Allow some spacing
        result = subprocess.run(
            real_command, 
            shell=True, 
            env=env,
            text=True,
            capture_output=False  # Let it stream to stdout
        )
        if result.returncode != 0:
            print(f"{Colors.RED}Command failed with exit code {result.returncode}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error executing command: {e}{Colors.RESET}")
        
    print("") # Empty line for spacing
    time.sleep(1.5)

def main():
    root = os.path.abspath("demo_env")
    
    # Setup clean environment
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    
    original_cwd = os.getcwd()
    os.chdir(root)
    
    try:
        # Intro
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Data Time Machine (DTM) Demo ==={Colors.RESET}\n")
        time.sleep(1)

        # 1. Init
        run_step("", "dtm init")

        # 2. Create data
        sys.stdout.write(f"{Colors.GREEN}user@dtm-demo{Colors.RESET}:{Colors.BLUE}~/data-project{Colors.RESET}$ ")
        type_print("echo 'id,value' > data.csv && echo '1,100' >> data.csv", delay=0.05)
        with open("data.csv", "w") as f:
            f.write("id,value\n1,100\n")
        time.sleep(0.5)
        print("") 
        
        run_step("", "cat data.csv")

        # 3. Snapshot
        run_step("", "dtm snapshot -m 'Initial working state'")

        # 4. Corrupt data
        sys.stdout.write(f"{Colors.GREEN}user@dtm-demo{Colors.RESET}:{Colors.BLUE}~/data-project{Colors.RESET}$ ")
        type_print("# Simulating a bad data pipeline run...", delay=0.05)
        time.sleep(1)
        with open("data.csv", "w") as f:
            f.write("id,value\n1,ERROR_NULL\n")
        print("\n")
        
        run_step("", "cat data.csv")
        
        # 5. Restore
        # We need the commit ID. In a real shell user would copy paste. 
        # Here we programmatically find it but pretend to type it.
        # Let's just list log first
        run_step("", "dtm log")
        
        # Get the commit ID quietly
        env = os.environ.copy()
        env["PYTHONPATH"] = original_cwd
        out = subprocess.run(f"{sys.executable} -m src.cli log", shell=True, env=env, capture_output=True, text=True).stdout
        # Assuming the first line has the commit hash "Commit: <hash>"
        for line in out.splitlines():
            if "Commit:" in line:
                latest_commit = line.split("Commit:")[1].strip().split()[0] # simplified parsing
                break
        
        run_step("", f"dtm checkout {latest_commit}")

        # 6. Verify verify
        run_step("", "cat data.csv")
        
        print(f"{Colors.BOLD}{Colors.GREEN}Recovery Successful!{Colors.RESET}\n")
        
    finally:
        os.chdir(original_cwd)
        # Cleanup can be optional if we want to inspect artifacts

if __name__ == "__main__":
    main()
