from unittest.mock import MagicMock, patch

import pytest

from launch.lib.github.repo import get_github_repos  # Adjust to your actual import


@pytest.fixture
def authenticated_user_mock():
    user_mock = MagicMock()
    user_mock.get_repos.return_value = [MagicMock() for _ in range(3)]
    return user_mock


def test_get_github_repos_with_authenticated_user(authenticated_user_mock):
    with patch("launch.lib.github.repo.Github") as github_mock:
        repos = get_github_repos(github_mock, authenticated_user_mock)
        assert len(repos) == 3
        authenticated_user_mock.get_repos.assert_called_once()
