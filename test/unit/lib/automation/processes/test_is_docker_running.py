import subprocess
import unittest
from unittest.mock import MagicMock, patch

from launch.lib.automation.processes.functions import is_docker_running


class TestIsDockerRunning(unittest.TestCase):
    def test_is_docker_running_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = is_docker_running()

            mock_run.assert_called_once_with(
                ["docker", "ps"],
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertTrue(result)

    def test_is_docker_running_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ["docker", "ps"])

            result = is_docker_running()

            mock_run.assert_called_once_with(
                ["docker", "ps"],
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertFalse(result)
