import subprocess

import pytest

from launch.lib.automation.processes.functions import start_docker


def mock_dependencies(mocker, is_running=False):
    mocker.patch(
        "launch.lib.automation.processes.functions.is_docker_running",
        return_value=is_running,
    )
    mocker.patch("subprocess.Popen")
    mocker.patch("launch.lib.service.functions.click.secho")
    mocker.patch("time.sleep")


def test_start_docker_dry_run(mocker):
    mock_dependencies(mocker, is_running=False)
    start_docker(dry_run=True)


def test_start_docker_non_dry_run(mocker):
    mock_dependencies(mocker, is_running=False)
    mocker.patch("subprocess.Popen", return_value=mocker.MagicMock())
    start_docker(dry_run=False)


def test_start_docker_already_running(mocker):
    mock_dependencies(mocker, is_running=True)
    start_docker(dry_run=False)
