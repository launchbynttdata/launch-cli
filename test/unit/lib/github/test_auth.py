import pytest

from launch.lib.github import auth


def test_read_github_token():
    """Validates that our fixture is working correctly."""
    assert auth.read_github_token() == "ghp_test_value"


def test_read_github_token_missing_env(no_github_token):
    with pytest.raises(RuntimeError, match="is not set"):
        # Best practice for testing any function decorated with an LRU cache is to clear it first.
        auth.read_github_token.cache_clear()
        auth.read_github_token()


def test_github_headers():
    auth.github_headers.cache_clear()
    result = auth.github_headers()
    assert result.get("Authorization") == "Bearer ghp_test_value"
