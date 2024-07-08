import subprocess
from unittest.mock import mock_open

import pytest

from launch.lib.automation.common.functions import install_tool_versions


def test_install_tool_versions_success(mocker):
    mocker.patch("builtins.open", mock_open(read_data="tool1\n tool2"))
    mock_run = mocker.patch("subprocess.run")

    install_tool_versions("fake_file")

    mock_run.assert_has_calls(
        [
            mocker.call(["asdf", "plugin", "add", "tool1"]),
            mocker.call(["asdf", "plugin", "add", "tool2"]),
            mocker.call(["asdf", "install"]),
        ]
    )


def test_install_tool_versions_file_read_exception(mocker):
    mocker.patch("builtins.open", side_effect=IOError("File not found"))

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")


def test_install_tool_versions_subprocess_exception(mocker):
    mocker.patch("builtins.open", mock_open(read_data="tool1\n tool2"))
    mocker.patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, ["asdf"])
    )

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")
