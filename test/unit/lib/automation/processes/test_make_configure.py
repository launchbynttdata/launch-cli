import subprocess
from unittest.mock import patch

import pytest

from launch.lib.automation.processes.functions import make_configure


def test_make_configure_success():
    with patch("subprocess.run") as mock_run:
        make_configure()
        mock_run.assert_called_once_with(["make", "configure"], check=True)


def test_make_configure_failure():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc_info:
        mock_run.side_effect = subprocess.CalledProcessError(1, "make configure")
        make_configure()
        assert "An error occurred:" in str(exc_info.value)
