import pytest
from git.repo import Repo

from launch.lib.local_repo.branch import get_current_branch_name


def test_get_current_branch_name_succeeds_in_git_repo(tmp_path):
    Repo.init(path=tmp_path, initial_branch="main")
    assert get_current_branch_name(repo_path=tmp_path) == "main"


def test_get_current_branch_name_fails_if_not_git_repo(tmp_path):
    with pytest.raises(Exception):
        get_current_branch_name(repo_path=tmp_path)
