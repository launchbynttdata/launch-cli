import pytest
import json
from unittest.mock import patch, mock_open

from launch.lib.service.common import load_launchconfig


def test_load_launchconfig_success(fakedata):
    mock_file_content = json.dumps(fakedata)

    mock_open_function = mock_open(read_data=mock_file_content)
    with patch("builtins.open", mock_open_function):
        with patch("launch.lib.service.common.input_data_validation", return_value=fakedata):
            result = load_launchconfig("fake_path.json")
            assert result == fakedata


def test_load_launchconfig_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_launchconfig("fake_path.json")


def test_load_launchconfig_invalid_json():
    mock_file_content = "{invalid json}"

    mock_open_function = mock_open(read_data=mock_file_content)
    with patch("builtins.open", mock_open_function):
        with pytest.raises(json.JSONDecodeError):
            load_launchconfig("fake_path.json")


def test_load_launchconfig_validation_error(fakedata):
    mock_file_content = json.dumps(fakedata)

    mock_open_function = mock_open(read_data=mock_file_content)
    with patch("builtins.open", mock_open_function):
        with patch("launch.lib.service.common.input_data_validation", side_effect=Exception("Validation error")):
            with pytest.raises(Exception, match="Validation error"):
                load_launchconfig("fake_path.json")
