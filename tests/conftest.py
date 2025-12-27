import os
import pytest
import shutil
import tempfile

@pytest.fixture
def temp_workspace():
    """Creates a temporary workspace and cleans it up after."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)

@pytest.fixture
def dtm_repo(temp_workspace):
    """Initializes a DTM repo in the temp workspace."""
    from src.core.metadata import MetadataManager
    meta = MetadataManager(temp_workspace)
    meta.init_repo()
    return meta
