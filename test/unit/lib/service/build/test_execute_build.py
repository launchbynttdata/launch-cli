import pytest

from pathlib import Path
from unittest.mock import patch
from launch.lib.service.build import execute_build


def test_execute_build_no_push():
    service_dir = Path("/fake/dir")

    with patch("os.chdir") as mock_chdir, patch("builtins.print") as mock_print, patch(
        "start_docker"
    ) as mock_start_docker, patch("git_config") as mock_git_config, patch(
        "make_configure"
    ) as mock_make_configure, patch(
        "make_build"
    ) as mock_make_build, patch(
        "make_docker_aws_ecr_login"
    ) as mock_make_docker_aws_ecr_login, patch(
        "make_push"
    ) as mock_make_push:
        execute_build(service_dir=service_dir, push=False, dry_run=True)

        mock_chdir.assert_called_once_with(service_dir)
        mock_print.assert_called_once_with(f"Building service in {service_dir}")
        mock_start_docker.assert_called_once_with(dry_run=True)
        mock_git_config.assert_called_once_with(dry_run=True)
        mock_make_configure.assert_called_once_with(dry_run=True)
        mock_make_build.assert_called_once_with(dry_run=True)
        mock_make_docker_aws_ecr_login.assert_not_called()
        mock_make_push.assert_not_called()


def test_execute_build_with_push_aws():
    service_dir = Path("/fake/dir")

    with patch("os.chdir") as mock_chdir, patch("builtins.print") as mock_print, patch(
        "start_docker"
    ) as mock_start_docker, patch("git_config") as mock_git_config, patch(
        "make_configure"
    ) as mock_make_configure, patch(
        "make_build"
    ) as mock_make_build, patch(
        "make_docker_aws_ecr_login"
    ) as mock_make_docker_aws_ecr_login, patch(
        "make_push"
    ) as mock_make_push:
        execute_build(service_dir=service_dir, push=True, dry_run=True)

        mock_chdir.assert_called_once_with(service_dir)
        mock_print.assert_called_once_with(f"Building service in {service_dir}")
        mock_start_docker.assert_called_once_with(dry_run=True)
        mock_git_config.assert_called_once_with(dry_run=True)
        mock_make_configure.assert_called_once_with(dry_run=True)
        mock_make_build.assert_called_once_with(dry_run=True)
        mock_make_docker_aws_ecr_login.assert_called_once_with(dry_run=True)
        mock_make_push.assert_called_once_with(dry_run=True)
