import subprocess
from unittest.mock import patch
import pytest
from launch.lib.automation.processes.functions import git_config

def test_git_config_dry_run():
    with patch("click.secho") as mock_secho, patch("subprocess.run") as mock_run:
        git_config(dry_run=True)
        mock_secho.assert_any_call(f"[DRYRUN] Would have ran subprocess: git config", fg="yellow")
        mock_run.assert_not_called()

def test_git_config_success():
    with patch("click.secho") as mock_secho, patch("subprocess.run") as mock_run:
        git_config(dry_run=False)
        mock_secho.assert_any_call(f"Running make git config")
        assert mock_run.call_count == 2
        mock_run.assert_any_call(["git", "config", "--global", "user.name", "nobody"], check=True)
        mock_run.assert_any_call(["git", "config", "--global", "user.email", "nobody@nttdata.com"], check=True)

def test_git_config_failure():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git config")
        with pytest.raises(RuntimeError) as exc_info:
            git_config(dry_run=False)
        assert "An error occurred:" in str(exc_info.value)