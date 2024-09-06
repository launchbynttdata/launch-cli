import subprocess
from unittest.mock import mock_open

import pytest

from launch.lib.automation.environment.functions import (
    install_tool_versions,
    parse_plugin_line,
)

EXAMPLE_TOOL_VERSIONS = """
tool1 1.0.0
tool2 2.0.0
tool3 3.0.0-alpha #https://github.com/org/tool3
tool4 4.0.0-beta # https://github.com/org/tool4
"""


def test_install_tool_versions_success(mocker):
    mocker.patch("builtins.open", mock_open(read_data=EXAMPLE_TOOL_VERSIONS))
    mock_run = mocker.patch("subprocess.run")

    install_tool_versions("fake_file")

    mock_run.assert_has_calls(
        [
            mocker.call(["asdf", "plugin", "add", "tool1"]),
            mocker.call(["asdf", "plugin", "add", "tool2"]),
            mocker.call(
                ["asdf", "plugin", "add", "tool3", "https://github.com/org/tool3"]
            ),
            mocker.call(
                ["asdf", "plugin", "add", "tool4", "https://github.com/org/tool4"]
            ),
            mocker.call(["asdf", "install"]),
        ]
    )


def test_install_tool_versions_file_read_exception(mocker):
    mocker.patch("builtins.open", side_effect=IOError("File not found"))

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")


def test_install_tool_versions_subprocess_exception(mocker):
    mocker.patch("builtins.open", mock_open(read_data=EXAMPLE_TOOL_VERSIONS))
    mocker.patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, ["asdf"])
    )

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")


@pytest.mark.parametrize(
    "line, expected",
    [
        ("pre-commit 3.3.3", ("pre-commit", "3.3.3", None)),
        ("pre-commit 3.3.3 # just a comment, not a URL", ("pre-commit", "3.3.3", None)),
        (
            "repo-tool v2.10.3-launch # https://github.com/launchbynttdata/asdf-repo-tool",
            (
                "repo-tool",
                "v2.10.3-launch",
                "https://github.com/launchbynttdata/asdf-repo-tool",
            ),
        ),
        (
            "repo-tool v2.10.3-launch #https://github.com/launchbynttdata/asdf-repo-tool",
            (
                "repo-tool",
                "v2.10.3-launch",
                "https://github.com/launchbynttdata/asdf-repo-tool",
            ),
        ),
    ],
)
def test_parse_plugin_line(line, expected):
    assert parse_plugin_line(line) == expected
