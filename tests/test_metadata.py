import os
from datetime import datetime
from src.core.metadata import MetadataManager, Commit, FileObject

def test_init_repo(temp_workspace):
    manager = MetadataManager(temp_workspace)
    manager.init_repo()
    
    assert os.path.exists(os.path.join(temp_workspace, ".dtm"))
    assert os.path.exists(os.path.join(temp_workspace, ".dtm", "objects"))
    assert os.path.exists(os.path.join(temp_workspace, ".dtm", "commits"))
    assert os.path.exists(os.path.join(temp_workspace, ".dtm", "HEAD"))

def test_save_and_get_commit(dtm_repo):
    commit = Commit(
        id="abc1234",
        message="Test commit",
        objects={}
    )
    dtm_repo.save_commit(commit)
    
    loaded = dtm_repo.get_commit("abc1234")
    assert loaded.id == "abc1234"
    assert loaded.message == "Test commit"

def test_get_head_ref_defaults(dtm_repo):
    assert dtm_repo.get_head_ref() == "refs/heads/main"

def test_generate_commit_id(dtm_repo):
    cid = dtm_repo.generate_commit_id(None, "msg", datetime.now())
    assert len(cid) == 40 # SHA1 length
