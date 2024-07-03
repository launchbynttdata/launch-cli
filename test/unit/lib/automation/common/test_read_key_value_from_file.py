import json
from unittest.mock import mock_open, patch

import pytest

from launch.lib.automation.common.functions import read_key_value_from_file


def test_read_key_value_from_file_success():
    test_data = {"testKey": "testValue"}
    mock_file = mock_open(read_data=json.dumps(test_data))

    with patch("builtins.open", mock_file):
        with patch("json.load", return_value=test_data):
            result = read_key_value_from_file("fake_file", "testKey")

    assert result == "testValue"


def test_read_key_value_from_file_key_error():
    test_data = {"anotherKey": "testValue"}
    mock_file = mock_open(read_data=json.dumps(test_data))

    with patch("builtins.open", mock_file):
        with patch("json.load", return_value=test_data):
            with pytest.raises(KeyError, match="No key found: testKey"):
                read_key_value_from_file("fake_file", "testKey")


def test_read_key_value_from_file_not_found_error():
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError, match="File not found: fake_file"):
            read_key_value_from_file("fake_file", "testKey")
