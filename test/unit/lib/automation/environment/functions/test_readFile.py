from unittest import mock

import pytest

from launch.lib.automation.environment.functions import readFile


def test_readFile_key_found(mocker):
    mock_file_content = 'export TEST_KEY="test_value"\n'
    mocker.patch("builtins.open", mock.mock_open(read_data=mock_file_content))

    result = readFile("TEST_KEY", "dummy_path")
    assert result == "test_value"


def test_readFile_key_not_found(mocker):
    mock_file_content = 'export ANOTHER_KEY="another_value"\n'
    mocker.patch("builtins.open", mock.mock_open(read_data=mock_file_content))

    result = readFile("TEST_KEY", "dummy_path")
    assert result is None


def test_readFile_file_not_found(mocker):
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    mocker.patch("click.secho")  # Mock click.secho to avoid actual print in test

    result = readFile("TEST_KEY", "dummy_path")
    assert result is None
