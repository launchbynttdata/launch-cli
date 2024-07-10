import subprocess
from unittest.mock import MagicMock, patch

import pytest

from launch.lib.automation.terragrunt.functions import terragrunt_apply


@pytest.fixture(scope="function")
@patch("subprocess.run")
def test_terragrunt_apply_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file=None, run_all=True, dry_run=False)
    mock_run.assert_called_once_with(
        [
            "terragrunt",
            "run_all",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ],
        check=True,
    )


@patch("subprocess.run")
def test_terragrunt_apply_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file=None, run_all=False, dry_run=False)
    mock_run.assert_called_once_with(
        ["terragrunt", "apply", "-auto-approve", "--terragrunt-non-interactive"],
        check=True,
    )


@patch("subprocess.run")
def test_terragrunt_apply_with_file(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file="vars.tfvars", run_all=False, dry_run=False)
    mock_run.assert_called_once_with(
        [
            "terragrunt",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
            "-var-file",
            "vars.tfvars",
        ],
        check=True,
    )


@patch("subprocess.run")
def test_terragrunt_apply_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
    with pytest.raises(RuntimeError):
        terragrunt_apply(dry_run=False)
