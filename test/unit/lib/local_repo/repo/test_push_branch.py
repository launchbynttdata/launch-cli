from unittest.mock import MagicMock, patch

import pytest

from launch.lib.local_repo.repo import push_branch


@pytest.fixture
def repository():
    repo = MagicMock()
    repo.git.add = MagicMock()
    repo.git.commit = MagicMock()
    repo.git.push = MagicMock()
    return repo


def test_push_branch_success(repository):
    branch = "feature-branch"
    commit_msg = "Add new feature"

    with patch("launch.lib.local_repo.repo.logger.info") as mock_logger_info:
        push_branch(repository, branch, commit_msg)
        mock_logger_info.assert_called_once_with(
            f"{repository=}, {branch=}, {commit_msg=}"
        )
        repository.git.add.assert_called_once_with(["."])
        repository.git.commit.assert_called_once_with(["-m", commit_msg])
        repository.git.push.assert_called_once_with(
            ["--set-upstream", "origin", branch]
        )


def test_push_branch_default_commit_msg(repository):
    branch = "hotfix-branch"
    with patch("launch.lib.local_repo.repo.logger.info") as mock_logger_info:
        push_branch(repository, branch)
        mock_logger_info.assert_called_once_with(
            f"{repository=}, {branch=}, commit_msg='Initial commit'"
        )
        repository.git.add.assert_called_once_with(["."])
        repository.git.commit.assert_called_once_with(["-m", "Initial commit"])
        repository.git.push.assert_called_once_with(
            ["--set-upstream", "origin", branch]
        )
