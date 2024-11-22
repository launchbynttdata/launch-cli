import subprocess

import pytest

from launch.lib.automation.processes.functions import start_docker


def test_start_docker_dry_run(mocker):
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    start_docker(dry_run=True)
    mock_click_secho.assert_called_once_with(f"Starting docker if not running")


def test_start_docker_non_dry_run(mocker):
    mocker.patch(
        "launch.lib.automation.processes.functions.is_docker_running",
        return_value=False,
    )
    mock_popen = mocker.patch("subprocess.Popen")
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    mock_sleep = mocker.patch("time.sleep")

    mock_popen_instance = mocker.MagicMock()
    mock_popen.return_value = mock_popen_instance

    start_docker(dry_run=False)

    mock_click_secho.assert_called_once_with(f"Starting docker if not running")
    mock_popen.assert_called_once_with(
        ["dockerd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
    )
    mock_sleep.assert_called_once_with(5)


def test_start_docker_already_running(mocker):
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    start_docker(dry_run=False)
    mock_click_secho.assert_called_once_with(f"Starting docker if not running")
