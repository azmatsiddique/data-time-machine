import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class FileObject(BaseModel):
    """Represents a file tracked by DTM."""
    path: str
    content_hash: str
    size: int
    last_modified: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

class Commit(BaseModel):
    """A snapshot of the environment."""
    id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    objects: Dict[str, FileObject] = Field(default_factory=dict) # Map path -> FileObject

class Branch(BaseModel):
    """A named pointer to a commit."""
    name: str
    commit_id: Optional[str] = None

class MetadataManager:
    """Manages the state of the DTM repository."""
    
    DTM_DIR = ".dtm"
    OBJECTS_DIR = "objects"
    COMMITS_DIR = "commits"
    REFS_DIR = "refs"
    HEAD_FILE = "HEAD"

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.dtm_path = os.path.join(self.root_dir, self.DTM_DIR)

    def init_repo(self):
        """Initialize the .dtm directory structure."""
        if os.path.exists(self.dtm_path):
            raise FileExistsError("DTM repository already exists.")
        
        os.makedirs(os.path.join(self.dtm_path, self.OBJECTS_DIR))
        os.makedirs(os.path.join(self.dtm_path, self.COMMITS_DIR))
        os.makedirs(os.path.join(self.dtm_path, self.REFS_DIR, "heads"))
        
        # Set default branch to main
        self._write_head("refs/heads/main")
        print(f"Initialized DTM repository in {self.dtm_path}")

    def _write_head(self, ref: str):
        with open(os.path.join(self.dtm_path, self.HEAD_FILE), "w") as f:
            f.write(ref)

    def get_head_ref(self) -> str:
        """Returns the current ref (e.g., refs/heads/main)."""
        head_path = os.path.join(self.dtm_path, self.HEAD_FILE)
        if not os.path.exists(head_path):
            return "refs/heads/main" # Default
        with open(head_path, "r") as f:
            return f.read().strip()

    def get_current_commit_id(self) -> Optional[str]:
        """Resolves HEAD to a commit ID."""
        ref = self.get_head_ref()
        if ref.startswith("refs/"):
            ref_path = os.path.join(self.dtm_path, ref)
            if os.path.exists(ref_path):
                with open(ref_path, "r") as f:
                    return f.read().strip()
        return None # Detached HEAD or empty branch

    def save_commit(self, commit: Commit):
        """Saves a commit object to disk."""
        commit_path = os.path.join(self.dtm_path, self.COMMITS_DIR, commit.id)
        with open(commit_path, "w") as f:
            f.write(commit.model_dump_json(indent=2))
        
        # Update current branch ref
        ref = self.get_head_ref()
        if ref.startswith("refs/"):
            ref_path = os.path.join(self.dtm_path, ref)
            os.makedirs(os.path.dirname(ref_path), exist_ok=True)
            with open(ref_path, "w") as f:
                f.write(commit.id)

    def get_commit(self, commit_id: str) -> Commit:
        commit_path = os.path.join(self.dtm_path, self.COMMITS_DIR, commit_id)
        if not os.path.exists(commit_path):
            raise ValueError(f"Commit {commit_id} not found.")
        
        with open(commit_path, "r") as f:
            return Commit.model_validate_json(f.read())
    
    def generate_commit_id(self, parent_id: Optional[str], message: str, timestamp: datetime) -> str:
        """Simple hash generation for commit ID."""
        data = f"{parent_id}{message}{timestamp.isoformat()}"
        return hashlib.sha1(data.encode()).hexdigest()
