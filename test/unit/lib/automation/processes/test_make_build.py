import os
import subprocess
from unittest.mock import patch

import pytest

from launch.lib.automation.processes.functions import make_build


def test_make_build_success():
    with patch("subprocess.run") as mock_run:
        make_build(dry_run=False)
        mock_run.assert_called_once_with(
            ["make", "build"], env=os.environ.copy(), check=True
        )


def test_make_build_failure():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc_info:
        mock_run.side_effect = subprocess.CalledProcessError(1, "make build")
        make_build(dry_run=False)
        assert "An error occurred:" in str(exc_info.value)
