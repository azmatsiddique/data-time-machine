import os
import json
from typing import Dict, Optional
from src.core.backends import StorageBackend, S3Backend, GCSBackend, AzureBackend, LocalBackend
from src.core.metadata import MetadataManager

class RemoteManager:
    CONFIG_FILE = "config"
    REMOTES_KEY = "remotes"

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.dtm_dir = os.path.join(self.root_dir, ".dtm")
        self.config_path = os.path.join(self.dtm_dir, self.CONFIG_FILE)
        self.metadata = MetadataManager(root_dir)

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _save_config(self, config: dict):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def add_remote(self, name: str, uri: str):
        config = self._load_config()
        remotes = config.get(self.REMOTES_KEY, {})
        remotes[name] = uri
        config[self.REMOTES_KEY] = remotes
        self._save_config(config)

    def get_remote_uri(self, name: str) -> Optional[str]:
        config = self._load_config()
        return config.get(self.REMOTES_KEY, {}).get(name)

    def _get_backend_for_uri(self, uri: str) -> StorageBackend:
        # Simple URI parsing: scheme://bucket/prefix
        # s3://mybucket/prefix
        # gcs://mybucket/prefix
        # azure://container/prefix?connection_string=... (handling conn string is complex in URI)
        # For Azure, maybe user provides container name and we expect env var?
        # Let's assume standard URI parsing.
        
        # Local: local:///path/to/repo or just /path...
        
        if uri.startswith("s3://"):
             # s3://bucket/path
             parts = uri[5:].split("/", 1)
             bucket = parts[0]
             prefix = parts[1] if len(parts) > 1 else ""
             return S3Backend(bucket, prefix)
        elif uri.startswith("gs://") or uri.startswith("gcs://"):
             parts = uri.replace("gs://", "").replace("gcs://", "").split("/", 1)
             bucket = parts[0]
             prefix = parts[1] if len(parts) > 1 else ""
             return GCSBackend(bucket, prefix)
        elif uri.startswith("azure://"):
             # azure://container/prefix
             parts = uri[8:].split("/", 1)
             container = parts[0]
             prefix = parts[1] if len(parts) > 1 else ""
             return AzureBackend(container, prefix=prefix)
        else:
             # Assume local
             path = uri.replace("file://", "")
             return LocalBackend(os.path.join(path, ".dtm"))
             # Wait, a remote repo has .dtm structure too?
             # If pushing to "remote directory", it should probably act like a bare repo or normal DTM repo.
             # Let's assume it has standard DTM structure objects/, commits/
             
    def push(self, remote_name: str):
        uri = self.get_remote_uri(remote_name)
        if not uri:
            raise ValueError(f"Remote {remote_name} not found")
            
        backend = self._get_backend_for_uri(uri)
        
        # 1. Push Commits
        # Scan local commits
        commits_dir = os.path.join(self.dtm_dir, "commits")
        for commit_file in os.listdir(commits_dir):
            # We should probably only push ancestors of HEAD?
            # For MVP, push ALL commits.
            local_path = os.path.join(commits_dir, commit_file)
            remote_key = f"commits/{commit_file}"
            
            # Simple optimization: if backend supports exists, check it.
            # But commit metadata is small, overwriting is fine.
            with open(local_path, "rb") as f:
                data = f.read()
            backend.put(remote_key, data)
            
        # 2. Push Objects
        # We need to parse all commits to find all objects?
        # Or just push everything in .dtm/objects?
        # Pushing everything is easiest for MVP.
        objects_dir = os.path.join(self.dtm_dir, "objects")
        for obj_file in os.listdir(objects_dir):
            if obj_file in {".DS_Store"}: continue
            
            remote_key = f"objects/{obj_file}"
            if not backend.exists(remote_key):
                local_path = os.path.join(objects_dir, obj_file)
                # Directly upload the file (it's already compressed gzipped blob)
                backend.put_file(remote_key, local_path)
                
        # 3. Push Refs (HEAD)
        # TODO: Support branches mapping. For now, push current HEAD to remote HEAD.
        head_ref = self.metadata.get_head_ref() # e.g. refs/heads/main
        if head_ref.startswith("refs/"):
             # Read the ref content (commit ID)
             ref_path = os.path.join(self.dtm_dir, head_ref)
             with open(ref_path, "rb") as f:
                 data = f.read()
             backend.put(head_ref, data) # Store at same path refs/heads/main
             
        print(f"Pushed to {uri}")

    def pull(self, remote_name: str):
        uri = self.get_remote_uri(remote_name)
        if not uri:
            raise ValueError(f"Remote {remote_name} not found")
            
        backend = self._get_backend_for_uri(uri)
        
        # This is harder because "listing" via backend abstraction is not implemented!
        # StorageBackend needs list() method to know what to pull.
        # OR we rely on traversing from HEAD.
        
        # 1. Fetch remote HEAD
        # We assume remote follows same structure
        # Getting generic refs is tricky without listing.
        # Let's assume we pull 'refs/heads/main'.
        
        try:
             main_ref_data = backend.get("refs/heads/main")
             remote_head_id = main_ref_data.decode().strip()
             
             # Store this ref locally as refs/remotes/origin/main?
             # For MVP, let's just fetch objects for this commit chain.
             self._fetch_commit_chain(backend, remote_head_id)
             
             # fast-forward local HEAD if possible? 
             # Or just leave them in repo for checkout.
             print(f"Pulled from {uri}. Remote HEAD is at {remote_head_id}")
             
        except Exception as e:
            print(f"Failed to pull ref: {e}")

    def _fetch_commit_chain(self, backend: StorageBackend, commit_id: str):
        # BFS/DFS to fetch commits and objects
        import queue
        q = queue.Queue()
        q.put(commit_id)
        
        # Track visited to avoid cycles/redundancy
        visited = set()
        
        while not q.empty():
            cid = q.get()
            if cid in visited: continue
            
            # Check if we have it locally
            local_commit_path = os.path.join(self.dtm_dir, "commits", cid)
            if os.path.exists(local_commit_path):
                 # We have this commit.
                 # Should we assume we have its parent?
                 # If we have it, we stop traversing branch?
                 # Yes.
                 continue
            
            # Fetch commit
            try:
                commit_data = backend.get(f"commits/{cid}")
                # Save locally
                with open(local_commit_path, "wb") as f:
                    f.write(commit_data)
                
                # Parse commit
                from src.core.metadata import Commit
                commit = Commit.model_validate_json(commit_data)
                
                # Fetch objects
                for file_path, obj in commit.objects.items():
                    obj_hash = obj.content_hash
                    local_obj_path = os.path.join(self.dtm_dir, "objects", obj_hash)
                    if not os.path.exists(local_obj_path):
                         backend.get_file(f"objects/{obj_hash}", local_obj_path)
                         
                # Queue parent
                if commit.parent_id:
                    q.put(commit.parent_id)
                    
                visited.add(cid)
            except Exception as e:
                print(f"Error fetching commit {cid}: {e}")
