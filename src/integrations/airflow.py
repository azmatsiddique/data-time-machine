from typing import Optional
import logging

try:
    from airflow.models import BaseOperator
except ImportError:
    # If Airflow is not installed, we can define a dummy for local code verification,
    # but at runtime in Airflow it MUST succeed.
    # We'll allow failure if not importing for type checking.
    BaseOperator = object

# apply_defaults is deprecated/removed in recent Airflow. 
# We define a dummy to be safe if older code patterns copied it, 
# or just remove it. We'll remove it.

from src.core.controller import DTMController

class DTMSnapshotOperator(BaseOperator):
    """
    Airflow Operator to create a DTM snapshot.
    
    :param message: The commit message for the snapshot.
    :param repo_path: Path to the DTM repository (default: current working dir).
    """
    
    # In Airflow 2.0+, @apply_defaults is not needed if we call super().__init__
    def __init__(self, message: str, repo_path: str = ".", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.repo_path = repo_path

    def execute(self, context):
        self.log.info(f"Creating DTM snapshot for repo at {self.repo_path}")
        try:
            controller = DTMController(self.repo_path)
            commit_id = controller.snapshot(self.message)
            self.log.info(f"Snapshot created successfully: {commit_id}")
            return commit_id
        except Exception as e:
            self.log.error(f"Failed to create snapshot: {e}")
            raise
