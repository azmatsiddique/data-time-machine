try:
    from prefect import task, get_run_logger
except ImportError:
    # Dummy decorator and logger for systems without prefect
    def task(func=None, **kwargs):
        if func:
            return func
        def wrapper(f):
            return f
        return wrapper
        
    def get_run_logger():
        import logging
        return logging.getLogger("dtm.prefect")

from src.core.controller import DTMController

@task(name="create_dtm_snapshot")
def create_dtm_snapshot(message: str, repo_path: str = ".") -> str:
    """
    Prefect task to create a DTM snapshot.
    
    Args:
        message: Commit message.
        repo_path: Path to DTM repository.
        
    Returns:
        The commit_id of the new snapshot.
    """
    logger = get_run_logger()
    logger.info(f"Creating DTM snapshot for repo at {repo_path}")
    
    controller = DTMController(repo_path)
    try:
        commit_id = controller.snapshot(message)
        logger.info(f"Snapshot created successfully: {commit_id}")
        return commit_id
    except Exception as e:
        logger.error(f"Failed to create snapshot: {e}")
        raise
