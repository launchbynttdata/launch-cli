import subprocess

import pytest

from launch.lib.automation.processes.functions import start_docker


def mock_dependencies(mocker, is_running=False):
    mock_is_docker_running = mocker.patch(
        "launch.lib.automation.processes.functions.is_docker_running",
        return_value=is_running,
    )
    mock_popen = mocker.patch("subprocess.Popen")
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    mock_sleep = mocker.patch("time.sleep")
    return mock_is_docker_running, mock_popen, mock_click_secho, mock_sleep


def test_start_docker_dry_run(mocker):
    _, mock_popen, mock_click_secho, _ = mock_dependencies(mocker, is_running=False)

    start_docker(dry_run=True)

    mock_click_secho.assert_called_with(
        f"[DRYRUN] Would have started docker daemon", fg="yellow"
    )
    mock_popen.assert_not_called()


def test_start_docker_non_dry_run(mocker):
    _, mock_popen, mock_click_secho, mock_sleep = mock_dependencies(
        mocker, is_running=False
    )

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
    _, mock_popen, mock_click_secho, _ = mock_dependencies(mocker, is_running=True)

    start_docker(dry_run=False)

    mock_click_secho.assert_called_once_with(f"Starting docker if not running")
    mock_popen.assert_not_called()
