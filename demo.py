import os
import sys
import subprocess
import time

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    ret = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if ret.returncode != 0:
        print(f"Error: {ret.stderr}")
        sys.exit(1)
    return ret.stdout.strip()

def main():
    root = os.path.abspath("demo_env")
    
    # 1. Setup environment
    if os.path.exists(root):
        import shutil
        shutil.rmtree(root)
    os.makedirs(root)
    
    # We need to make sure 'dtm' is available. 
    # Since we haven't installed it, we'll run it via python -m src.cli
    # And we need PYTHONPATH to include the project root
    project_root = os.getcwd()
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    
    dtm_cmd = f"{sys.executable} -m src.cli"
    
    print(f"--- Setting up demo in {root} ---")
    
    # 2. Init DTM
    print("\n[1] Initializing DTM...")
    subprocess.run(f"{dtm_cmd} init", shell=True, cwd=root, env=env, check=True)
    
    # 3. Create initial data
    print("\n[2] Creating initial 'good' data...")
    data_file = os.path.join(root, "data.csv")
    with open(data_file, "w") as f:
        f.write("id,value\n1,100\n2,200\n")
    
    # 4. Snapshot
    print("\n[3] Snapshotting state...")
    out = subprocess.run(f"{dtm_cmd} snapshot -m 'Initial good state'", shell=True, cwd=root, env=env, capture_output=True, text=True, check=True)
    print(out.stdout)
    
    # Extract commit ID (assuming output format "Created snapshot: <id>")
    commit_id = out.stdout.strip().split(": ")[1]
    print(f"Saved commit: {commit_id}")
    
    # 5. Simulate corruption
    print("\n[4] Simulating data corruption (Pipeline Bug)...")
    time.sleep(1) # Ensure timestamp diff
    with open(data_file, "w") as f:
        f.write("id,value\n1,ERROR\n2,200\n")
    
    print("Current file content:")
    with open(data_file, "r") as f:
        print(f.read())
        
    # 6. Restore
    print(f"\n[5] Rolling back to {commit_id}...")
    subprocess.run(f"{dtm_cmd} checkout {commit_id}", shell=True, cwd=root, env=env, check=True)
    
    # 7. Verify
    print("\n[6] Verifying restoration...")
    with open(data_file, "r") as f:
        content = f.read()
        print("Restored file content:")
        print(content)
        
    if "1,100" in content:
        print("\nSUCCESS: Data Lineage Time Machine worked! Data rolled back.")
    else:
        print("\nFAILURE: Data was not restored correctly.")

if __name__ == "__main__":
    main()
