import logging
from unittest.mock import MagicMock, patch

import pytest
from git.exc import GitCommandError

from launch.lib.local_repo.repo import checkout_branch


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.git.checkout = MagicMock()
    return repo


def test_checkout_new_branch(mock_repository, mocker):
    init_branch = "development"
    with patch.object(logging, "info") as mock_log_info:
        checkout_branch(
            repository=mock_repository, target_branch=init_branch, new_branch=True
        )

    mock_repository.git.checkout.assert_called_once_with(["-b", init_branch])


def test_checkout_existing_branch(mock_repository, mocker):
    main_branch = "main"
    with patch.object(logging, "info") as mock_log_info:
        checkout_branch(repository=mock_repository, target_branch=main_branch)

    mock_repository.git.checkout.assert_called_once_with([main_branch])


def test_checkout_branch_exception(mock_repository, mocker):
    main_branch = "main"
    error_message = "error"
    mock_repository.git.checkout.side_effect = GitCommandError(
        "checkout", error_message
    )

    with pytest.raises(
        RuntimeError, match=f"An error occurred while checking out {main_branch}"
    ):
        checkout_branch(mock_repository, main_branch)
