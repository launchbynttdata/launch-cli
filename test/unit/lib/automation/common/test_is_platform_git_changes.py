from unittest.mock import MagicMock, patch

import pytest

from launch.lib.automation.common.functions import is_platform_git_changes


# Test when the commit hash is the same as the main branch
def test_commit_hash_same_as_main_branch():
    mock_repo = MagicMock()
    mock_repo.remote.return_value.fetch.return_value = None
    mock_repo.commit.return_value = MagicMock()
    mock_repo.rev_parse.return_value = "same_commit_hash"

    result = is_platform_git_changes(
        mock_repo, "same_commit_hash", "main", "infrastructure"
    )

    assert result


# Test when the commit hash is different from the main branch
def test_commit_hash_different_from_main_branch():
    mock_repo = MagicMock()
    commit_main = MagicMock()
    commit_compare = MagicMock()
    mock_repo.remote.return_value.fetch.return_value = None
    mock_repo.commit.side_effect = [commit_compare, commit_main]
    mock_repo.rev_parse.return_value = "different_commit_hash"

    # Setup diffs to simulate changes
    commit_compare.diff.return_value = MagicMock()

    result = is_platform_git_changes(
        mock_repo, "different_commit_hash", "infrastructure"
    )

    assert result


# Test when there are no git changes in the specified directory
def test_no_git_changes_in_directory():
    mock_repo = MagicMock()
    mock_repo.commit().diff.return_value = []

    result = is_platform_git_changes(mock_repo, "commit_hash", "infrastructure")
    assert not result


# Test when there are changes both inside and outside the specified directory
def test_changes_in_both_inside_and_outside_directory():
    mock_repo = MagicMock()
    diff_mock = MagicMock()
    diff_mock.diff.return_value = [
        MagicMock(a_path="infrastructure/file1"),
        MagicMock(a_path="other/file2"),
    ]
    mock_repo.commit.side_effect = [MagicMock(), diff_mock]

    with pytest.raises(
        RuntimeError,
        match="Changes found in both inside and outside dir: infrastructure",
    ):
        is_platform_git_changes(mock_repo, "commit_hash", "infrastructure")


# Test when there are changes only inside the specified directory
def test_changes_only_inside_directory():
    mock_repo = MagicMock()
    exclusive_dir_diff = [MagicMock(a_path="infrastructure/file1")]
    mock_repo.commit().diff.return_value = exclusive_dir_diff

    result = is_platform_git_changes(mock_repo, "commit_hash", "infrastructure")
    assert result
