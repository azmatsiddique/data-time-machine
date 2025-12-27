from datetime import datetime
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
        files = self.storage.scan_workspace()
        
        # 2. Store files and build objects map
        objects = {}
        for rel_path in files:
            content_hash, size = self.storage.store_file(rel_path)
            objects[rel_path] = FileObject(
                path=rel_path,
                content_hash=content_hash,
                size=size
            )
            
        # 3. Create Commit
        parent_id = self.metadata.get_current_commit_id()
        timestamp = datetime.now()
        commit_id = self.metadata.generate_commit_id(parent_id, message, timestamp)
        
        commit = Commit(
            id=commit_id,
            message=message,
            timestamp=timestamp,
            parent_id=parent_id,
            objects=objects
        )
        
        # 4. Save Commit
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
