import subprocess
from unittest.mock import patch

import pytest

from launch.lib.automation.processes.functions import make_push


def test_make_push_success():
    with patch("subprocess.run") as mock_run:
        make_push(dry_run=False)
        mock_run.assert_called_once_with(["make", "push"], check=True)


def test_make_push_failure():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc_info:
        mock_run.side_effect = subprocess.CalledProcessError(1, "make push")
        make_push(dry_run=False)
        assert "An error occurred:" in str(exc_info.value)
