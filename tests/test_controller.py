from datetime import time
from src.core.controller import DTMController

def test_snapshot_workflow(temp_workspace):
    ctrl = DTMController(temp_workspace)
    ctrl.init()
    
    # Create data
    with open("data.csv", "w") as f:
        f.write("a,b\n1,2")
        
    commit_id = ctrl.snapshot("Initial")
    assert commit_id is not None
    
    commit = ctrl.metadata.get_commit(commit_id)
    assert commit.message == "Initial"
    assert "data.csv" in commit.objects

def test_checkout_workflow(temp_workspace):
    ctrl = DTMController(temp_workspace)
    ctrl.init()
    
    # V1
    with open("config", "w") as f: f.write("v1")
    c1 = ctrl.snapshot("v1")
    
    # V2
    with open("config", "w") as f: f.write("v2")
    c2 = ctrl.snapshot("v2")
    
    # Checkout V1
    ctrl.checkout(c1)
    with open("config", "r") as f:
        assert f.read() == "v1"
        
    # Checkout V2
    ctrl.checkout(c2)
    with open("config", "r") as f:
        assert f.read() == "v2"
