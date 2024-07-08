import logging
from unittest.mock import MagicMock, patch

from launch.lib.github.repo import repo_exist


def test_repo_exist_true(mocker):
    mock_github = MagicMock()
    mock_github.get_repo.return_value = MagicMock()
    repo_name = "existing_repo"

    result = repo_exist(repo_name, mock_github)
    mock_github.get_repo.assert_called_once_with(repo_name)
    assert result is True


def test_repo_exist_false_and_logs_info(mocker):
    mock_github = MagicMock()
    mock_github.get_repo.side_effect = Exception("Repository does not exist")
    repo_name = "nonexistent_repo"

    with patch.object(logging, "info") as mock_log_info:
        result = repo_exist(repo_name, mock_github)
    mock_github.get_repo.assert_called_once_with(repo_name)
    assert result is False
