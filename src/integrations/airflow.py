from typing import Optional
try:
    from airflow.models import BaseOperator
    from airflow.utils.decorators import apply_defaults
except ImportError:
    # improvements: log warning or create dummy base
    class BaseOperator:
        def __init__(self, *args, **kwargs):
            import logging
            self.log = logging.getLogger("airflow.task")
            
    def apply_defaults(func):
        return func

from src.core.controller import DTMController

class DTMSnapshotOperator(BaseOperator):
    """
    Airflow Operator to create a DTM snapshot.
    
    :param message: The commit message for the snapshot.
    :param repo_path: Path to the DTM repository (default: current working dir).
    """
    
    @apply_defaults
    def __init__(self, message: str, repo_path: str = ".", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.repo_path = repo_path

    def execute(self, context):
        self.log.info(f"Creating DTM snapshot for repo at {self.repo_path}")
        controller = DTMController(self.repo_path)
        
        # Verify it's initialized
        # (Controller methods usually don't verify init explicitly except by failing, 
        # but we can try/catch)
        try:
            commit_id = controller.snapshot(self.message)
            self.log.info(f"Snapshot created successfully: {commit_id}")
            return commit_id
        except Exception as e:
            self.log.error(f"Failed to create snapshot: {e}")
            raise
