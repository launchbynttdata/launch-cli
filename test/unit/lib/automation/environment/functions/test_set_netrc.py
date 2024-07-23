import os
from pathlib import Path
from unittest.mock import mock_open

import pytest

from launch.lib.automation.environment.functions import set_netrc


@pytest.fixture
def netrc_path():
    return Path("/path/to/target/.netrc")


def test_set_netrc_success(mocker, netrc_path):
    # Mock the open function and os.chmod call
    mock_file_open = mock_open()
    mocker.patch("builtins.open", mock_file_open)
    mock_chmod = mocker.patch("os.chmod")

    set_netrc(
        "password123", "example.com", "username", netrc_path=netrc_path, dry_run=False
    )

    # Check if file was written correctly
    mock_file_open.assert_called_once_with(netrc_path, "a")
    handle = mock_file_open()
    handle.write.assert_has_calls(
        [
            mocker.call("machine example.com\n"),
            mocker.call("login username\n"),
            mocker.call("password password123\n"),
        ]
    )

    # Check if os.chmod was called correctly
    mock_chmod.assert_called_once_with(netrc_path, 0o600)


def test_set_netrc_exception_during_write(mocker, netrc_path):
    # Mock open to raise an exception
    mocker.patch("builtins.open", side_effect=IOError("File write error"))

    with pytest.raises(RuntimeError, match="An error occurred"):
        set_netrc(
            "password123",
            "example.com",
            "username",
            netrc_path=netrc_path,
            dry_run=False,
        )


def test_set_netrc_exception_during_chmod(mocker, netrc_path):
    # Mock the open function and os.chmod to raise an exception
    mocker.patch("builtins.open", mock_open())
    mocker.patch("os.chmod", side_effect=OSError("Permission error"))

    with pytest.raises(RuntimeError, match="An error occurred"):
        set_netrc(
            "password123",
            "example.com",
            "username",
            netrc_path=netrc_path,
            dry_run=False,
        )
