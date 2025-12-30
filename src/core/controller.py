from datetime import datetime
import difflib
from typing import List, Optional
from src.core.metadata import MetadataManager, Commit, FileObject
from src.core.storage import StorageEngine

class DTMController:
    def __init__(self, root_dir: str = "."):
        self.metadata = MetadataManager(root_dir)
        self.storage = StorageEngine(root_dir)

    def init(self):
        self.metadata.init_repo()

    def snapshot(self, message: str) -> str:
        """Creates a new commit with the current state of the workspace."""
        # 1. Scan workspace
        files_metadata = self.storage.scan_workspace()
        
        # 2. Get parent commit for optimization
        parent_id = self.metadata.get_current_commit_id()
        parent_commit = self.metadata.get_commit(parent_id) if parent_id else None
        parent_objects = parent_commit.objects if parent_commit else {}
        
        # 3. Store files and build objects map
        objects = {}
        for file_meta in files_metadata:
            rel_path = file_meta['path']
            size = file_meta['size']
            mtime = file_meta['mtime']
            
            # Optimization: Check if file unchanged
            if rel_path in parent_objects:
                parent_obj = parent_objects[rel_path]
                # Compare size and mtime (allow small float diff for mtime?)
                # Actually, if we just use approximate equality it might be better, 
                # but exact match is safer. If OS mtime resolution is good, exact match works.
                if parent_obj.size == size and abs(parent_obj.last_modified - mtime) < 0.001:
                    # Unchanged, reuse hash
                    objects[rel_path] = FileObject(
                        path=rel_path,
                        content_hash=parent_obj.content_hash,
                        size=size,
                        last_modified=mtime
                    )
                    continue
            
            # Changed or new, re-hash and store
            content_hash, _ = self.storage.store_file(rel_path)
            objects[rel_path] = FileObject(
                path=rel_path,
                content_hash=content_hash,
                size=size,
                last_modified=mtime
            )
            
        # 4. Create Commit
        timestamp = datetime.now()
        commit_id = self.metadata.generate_commit_id(parent_id, message, timestamp)
        
        commit = Commit(
            id=commit_id,
            message=message,
            timestamp=timestamp,
            parent_id=parent_id,
            objects=objects
        )
        
        # 5. Save Commit
        self.metadata.save_commit(commit)
        return commit_id

    def checkout(self, commit_id: str):
        """Restores the workspace to the state of the given commit."""
        # 1. Get Commit
        commit = self.metadata.get_commit(commit_id)
        
        # 2. Restore files
        # TODO: Clear workspace of untracked files?
        # For now, we only overwrite/restore tracked files.
        for rel_path, file_obj in commit.objects.items():
            self.storage.restore_file(file_obj.content_hash, rel_path)
            
        # 3. Update HEAD (Detached or Branch logic needed)
        # For MVP, just updating the file state is the visual part.
        # Ideally we update HEAD to point to this commit if it's a checkout.
        # If we are just peeking, maybe we don't update HEAD? 
        # But 'checkout' implies moving HEAD.
        # Since our HEAD logic in MetadataManager relies on branches, 
        # we might need to support detached HEAD there.
        # For now, let's just log it.
        print(f"Checked out commit {commit_id}")

    def log(self) -> List[Commit]:
        """Returns commit history starting from HEAD."""
        history = []
        current_id = self.metadata.get_current_commit_id()
        
        while current_id:
            try:
                commit = self.metadata.get_commit(current_id)
                history.append(commit)
                current_id = commit.parent_id
            except ValueError:
                break
        return history
        return history

    def diff(self, commit_a_id: str, commit_b_id: str) -> str:
        """Generates a diff between two commits."""
        commit_a = self.metadata.get_commit(commit_a_id)
        commit_b = self.metadata.get_commit(commit_b_id)
        
        files_a = commit_a.objects
        files_b = commit_b.objects
        
        all_files = set(files_a.keys()) | set(files_b.keys())
        diff_output = []
        
        for file_path in sorted(all_files):
            obj_a = files_a.get(file_path)
            obj_b = files_b.get(file_path)
            
            if obj_a and obj_b:
                if obj_a.content_hash != obj_b.content_hash:
                    # Modified
                    diff_output.append(self._diff_content(file_path, obj_a.content_hash, obj_b.content_hash))
            elif obj_a:
                # Deleted in B
                diff_output.append(f"Deleted: {file_path}")
            elif obj_b:
                # Added in B
                diff_output.append(f"Added: {file_path}")
                
        if not diff_output:
            return "No changes."
            
        return "\n".join(diff_output)

    def _diff_content(self, file_path: str, hash_a: str, hash_b: str) -> str:
        data_a = self.storage.read_object(hash_a)
        data_b = self.storage.read_object(hash_b)
        
        # Try decoding as utf-8
        try:
            text_a = data_a.decode('utf-8').splitlines()
            text_b = data_b.decode('utf-8').splitlines()
            
            diff = difflib.unified_diff(
                text_a, text_b, 
                fromfile=f"a/{file_path}", 
                tofile=f"b/{file_path}",
                lineterm=""
            )
            return "\n".join(diff)
        except UnicodeDecodeError:
            return f"Binary file modified: {file_path} ({hash_a[:7]} -> {hash_b[:7]})"
