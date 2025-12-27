import os
import hashlib
import shutil
from typing import Tuple, List, Set

class StorageEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.dtm_dir = os.path.join(self.root_dir, ".dtm")
        self.objects_dir = os.path.join(self.dtm_dir, "objects")
        
        # Default ignore list
        self.ignore_patterns = {".dtm", ".git", ".DS_Store", "__pycache__"}

    def _get_hash_path(self, content_hash: str) -> str:
        # We could do sharding (e.g. objects/ab/c123...) but for MVP flat is fine
        return os.path.join(self.objects_dir, content_hash)

    def hash_file(self, filepath: str) -> str:
        """Calculates SHA1 hash of a file."""
        sha1 = hashlib.sha1()
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def store_file(self, rel_path: str) -> Tuple[str, int]:
        """Stores a file in the object store. Returns (hash, size)."""
        abs_path = os.path.join(self.root_dir, rel_path)
        content_hash = self.hash_file(abs_path)
        size = os.path.getsize(abs_path)
        
        object_path = self._get_hash_path(content_hash)
        
        if not os.path.exists(object_path):
            shutil.copy2(abs_path, object_path)
            # Make read-only? 
            # os.chmod(object_path, 0o444) 
        
        return content_hash, size

    def restore_file(self, content_hash: str, rel_path: str):
        """Restores a file from the object store."""
        object_path = self._get_hash_path(content_hash)
        dest_path = os.path.join(self.root_dir, rel_path)
        
        if not os.path.exists(object_path):
            raise FileNotFoundError(f"Object {content_hash} missing for {rel_path}")
            
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(object_path, dest_path)

    def scan_workspace(self) -> List[str]:
        """Returns a list of all tracked files in the workspace (relative paths)."""
        tracked_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for f in files:
                if f in self.ignore_patterns:
                    continue
                
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, self.root_dir)
                
                # Double check ignore (e.g. ignored_dir/file)
                if any(p in rel_path.split(os.sep) for p in self.ignore_patterns):
                    continue
                    
                tracked_files.append(rel_path)
        return tracked_files

    def cleanup_workspace(self):
        """Removes all tracked files from workspace (dangerous!)."""
        # For checkout, we might want to clean up files not in the commit.
        # This implementation removes everything except hidden/ignored.
        for item in os.listdir(self.root_dir):
            if item in self.ignore_patterns:
                continue
            path = os.path.join(self.root_dir, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
