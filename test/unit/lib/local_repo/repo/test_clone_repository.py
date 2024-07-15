import logging
from unittest.mock import MagicMock, patch

import pytest
from git.exc import GitCommandError

from launch.lib.local_repo.repo import clone_repository


@pytest.fixture
def test_fakedata():
    return {
        "repository_url": "https://github.com/example/repo.git",
        "target": "/path/to/target",
        "branch": "main",
        "mock_repo": MagicMock(),
        "error_message": "error during cloning",
    }


def test_clone_repository_success(test_fakedata):
    with patch(
        "launch.lib.local_repo.repo.Repo.clone_from",
        return_value=test_fakedata["mock_repo"],
    ) as mock_clone_from:
        result = clone_repository(
            test_fakedata["repository_url"],
            test_fakedata["target"],
            test_fakedata["branch"],
        )
        mock_clone_from.assert_called_once_with(
            url=test_fakedata["repository_url"],
            to_path=test_fakedata["target"],
            branch=test_fakedata["branch"],
        )
        assert result == test_fakedata["mock_repo"]


def test_clone_repository_error(mocker, test_fakedata):
    mocker.patch(
        "launch.lib.local_repo.repo.Repo.clone_from",
        side_effect=GitCommandError("clone", test_fakedata["error_message"]),
    )
    with patch.object(logging, "error") as mock_log_error, pytest.raises(
        RuntimeError
    ) as exc_info:
        clone_repository(
            test_fakedata["repository_url"],
            test_fakedata["target"],
            test_fakedata["branch"],
        )

    url = test_fakedata["repository_url"]
    expected_error = f"Error occurred while cloning the repository from {url}"
    assert str(exc_info.value) == expected_error
