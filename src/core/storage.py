import os
import hashlib
import shutil
import gzip
from typing import Tuple, List, Set, BinaryIO

from typing import Tuple, List, Set, BinaryIO, Dict
from src.core.backends import LocalBackend, StorageBackend

class StorageEngine:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.dtm_dir = os.path.join(self.root_dir, ".dtm")
        self.objects_dir = os.path.join(self.dtm_dir, "objects")
        
        # Use LocalBackend for local object storage
        self.backend = LocalBackend(self.objects_dir)
        
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
        
        if not self.backend.exists(content_hash):
            # Compress to temp file before putting to backend
            # Note: Ideally backend handles stream, but we want to gzip locally first
            # The backend.put_file expects a file path.
            # We can just write directly to the objects dir if we know it's local,
            # but to respect abstraction, let's create a temp compressed file.
            # OR, since LocalBackend is just a wrapper around fs, 
            # and we want to control the file structure...
            
            # Let's simple use a temp path
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                with open(abs_path, 'rb') as f_in:
                    with gzip.open(tmp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                self.backend.put_file(content_hash, tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        return content_hash, size

    def restore_file(self, content_hash: str, rel_path: str):
        """Restores a file from the object store."""
        dest_path = os.path.join(self.root_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # We need to decompress.
        # Backend.get_file copies the (gzipped) object to a path.
        # We can copy to a temp path, then decompress to dest.
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
        try:
            self.backend.get_file(content_hash, tmp_path)
            
            # Try decompress
            try:
                with gzip.open(tmp_path, 'rb') as f_in:
                    with open(dest_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            except (OSError, gzip.BadGzipFile):
                # Fallback
                shutil.copy2(tmp_path, dest_path)
        finally:
             if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def scan_workspace(self) -> List[dict]:
        """Returns a list of all tracked files in the workspace with metadata."""
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
                
                stat = os.stat(abs_path)
                tracked_files.append({
                    "path": rel_path,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                })
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

    def read_object(self, content_hash: str) -> bytes:
        """Reads the content of an object."""
        try:
            raw_data = self.backend.get(content_hash)
            return gzip.decompress(raw_data)
        except (OSError, gzip.BadGzipFile):
            return raw_data
