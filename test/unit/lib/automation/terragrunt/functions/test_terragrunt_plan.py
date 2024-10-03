import subprocess
from unittest.mock import MagicMock, patch

import pytest

from launch.lib.automation.terragrunt.functions import terragrunt_plan


@pytest.fixture(scope="function")
@patch("subprocess.run")
def test_terragrunt_plan_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(
        out_file=None,
        run_all=False,
        dry_run=False,
    )
    mock_run.assert_called_once_with(["terragrunt", "run_all", "plan"], check=True)


@patch("subprocess.run")
def test_terragrunt_plan_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(
        out_file=None,
        run_all=False,
        dry_run=False,
    )
    mock_run.assert_called_once_with(["terragrunt", "plan"], check=True)


@patch("subprocess.run")
def test_terragrunt_plan_with_file(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(
        out_file="plan.out",
        run_all=False,
        dry_run=False,
    )
    mock_run.assert_called_once_with(
        ["terragrunt", "plan", "-out", "plan.out"], check=True
    )


@patch("subprocess.run")
def test_terragrunt_plan_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
    with pytest.raises(RuntimeError):
        terragrunt_plan(dry_run=False)
