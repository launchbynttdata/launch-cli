import os
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest

from launch.config.terragrunt import TERRAGRUNT_RUN_DIRS

# Constants for testing
from launch.config.webhook import (
    WEBHOOK_BUILD_SCRIPT,
    WEBHOOK_GIT_REPO_TAG,
    WEBHOOK_GIT_REPO_URL,
    WEBHOOK_ZIP,
)
from launch.lib.automation.terragrunt.functions import copy_webhook


@pytest.fixture
def mock_clone_repository(mocker):
    return mocker.patch("launch.lib.local_repo.repo.clone_repository")


@pytest.fixture
def mock_os_chdir(mocker):
    return mocker.patch("os.chdir")


@pytest.fixture
def mock_os_chmod(mocker):
    return mocker.patch("os.chmod")


@pytest.fixture
def mock_subprocess_run(mocker):
    return mocker.patch("subprocess.run")


@pytest.fixture
def mock_os_walk(mocker):
    return mocker.patch("os.walk")


@pytest.fixture
def mock_shutil_copy(mocker):
    return mocker.patch("shutil.copy")


def test_copy_webhook(
    mock_clone_repository,
    mock_os_chdir,
    mock_os_chmod,
    mock_subprocess_run,
    mock_os_walk,
    mock_shutil_copy,
):
    # Setup
    webhooks_path = Path("/fake/webhooks_path")
    build_path = Path("/fake/build_path")
    target_environment = "dev"
    dry_run = True

    mock_os_walk.return_value = [
        (
            str(
                build_path.joinpath(
                    TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment)
                )
            ),
            [],
            [],
        )
    ]

    # Call the function
    copy_webhook(webhooks_path, build_path, target_environment, dry_run)

    # Assertions
    mock_clone_repository.assert_called_with(
        repository_url=WEBHOOK_GIT_REPO_URL,
        target=webhooks_path,
        branch=WEBHOOK_GIT_REPO_TAG,
        dry_run=dry_run,
    )
    mock_os_chdir.assert_any_call(webhooks_path)
    mock_os_chmod.assert_called_once_with(
        webhooks_path.joinpath(WEBHOOK_BUILD_SCRIPT), 0o755
    )
    mock_subprocess_run.assert_called_once_with(
        [webhooks_path.joinpath(WEBHOOK_BUILD_SCRIPT)], check=True
    )
    mock_os_chdir.assert_any_call(Path.cwd())
    mock_shutil_copy.assert_called_once_with(
        webhooks_path.joinpath(WEBHOOK_ZIP),
        str(
            build_path.joinpath(
                TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment)
            )
        ),
    )
