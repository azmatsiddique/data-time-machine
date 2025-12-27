import os
from src.core.storage import StorageEngine

def test_hash_file(temp_workspace):
    storage = StorageEngine(temp_workspace)
    
    file_path = os.path.join(temp_workspace, "test.txt")
    with open(file_path, "w") as f:
        f.write("hello world")
        
    # Python's hashlib.sha1(b"hello world").hexdigest() 
    # = 2aae6c35c94fcfb415dbe95f408b9ce91ee846ed
    h = storage.hash_file(file_path)
    assert h == "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"

def test_store_and_restore(temp_workspace):
    storage = StorageEngine(temp_workspace)
    # Ensure dtm dir exists for objects
    os.makedirs(os.path.join(temp_workspace, ".dtm", "objects"))
    
    # Create file
    with open("data.txt", "w") as f:
        f.write("content")
        
    # Store
    text_hash, size = storage.store_file("data.txt")
    assert size == 7
    
    # Remove file
    os.remove("data.txt")
    
    # Restore
    storage.restore_file(text_hash, "data.txt")
    assert os.path.exists("data.txt")
    with open("data.txt", "r") as f:
        assert f.read() == "content"

def test_scan_workspace(temp_workspace):
    storage = StorageEngine(temp_workspace)
    
    with open("f1.txt", "w") as f: f.write("1")
    os.makedirs("sub")
    with open("sub/f2.txt", "w") as f: f.write("2")
    
    os.makedirs(".dtm")
    with open(".dtm/config", "w") as f: f.write("conf")
    
    files = storage.scan_workspace()
    assert set(files) == {"f1.txt", "sub/f2.txt"}
