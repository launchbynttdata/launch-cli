import subprocess

import pytest

from launch.lib.automation.processes.functions import start_docker


def test_start_docker_dry_run(mocker):
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    start_docker(dry_run=True)
    mock_click_secho.assert_called_once_with(f"Starting docker if not running")


def test_start_docker_dry_run(mocker):
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    start_docker(dry_run=True)
    mock_click_secho.assert_called_with(
        f"[DRYRUN] Would have started docker daemon", fg="yellow"
    )


def test_start_docker_already_running(mocker):
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")
    start_docker(dry_run=False)
    mock_click_secho.assert_called_once_with(f"Starting docker if not running")
