import json
from pathlib import Path
from unittest.mock import patch

import pytest

from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.service.common import determine_existing_uuid


def test_no_launch_config_and_no_force():
    with patch("builtins.quit", side_effect=SystemExit), patch(
        "pathlib.Path.exists", return_value=False
    ), patch("click.secho") as mock_secho:
        input_data = {"key": "value"}

        with pytest.raises(SystemExit):
            determine_existing_uuid(input_data, Path("/some/path"), force=False)

        mock_secho.assert_called_once_with(
            f"No {LAUNCHCONFIG_NAME} found in local directory. Use --force to recreate when running this command.",
            fg="red",
        )


def test_launch_config_does_not_exist_and_force():
    with patch("pathlib.Path.exists", return_value=False):
        input_data = {"key": "value"}

        result = determine_existing_uuid(input_data, Path("/some/path"), force=True)

        assert result == {"key": "value"}


def test_no_launch_config_and_force(capsys):
    with patch("pathlib.Path.exists", return_value=False):
        input_data = {"key": "value"}

        result = determine_existing_uuid(input_data, Path("/some/path"), force=True)

        assert result == {"key": "value"}
        captured = capsys.readouterr()
        assert f"No {LAUNCHCONFIG_NAME} found in local directory." not in captured.out


def test_launch_config_exists_and_no_force(capsys):
    with patch("builtins.quit", side_effect=SystemExit), patch(
        "pathlib.Path.exists", return_value=True
    ):
        input_data = {"key": "value"}
        result = determine_existing_uuid(input_data, Path("/some/path"), force=False)
        assert result == input_data
