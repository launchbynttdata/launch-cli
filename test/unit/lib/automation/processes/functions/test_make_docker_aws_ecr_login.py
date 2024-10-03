import subprocess
from unittest.mock import patch

import pytest

from launch.lib.automation.processes.functions import make_docker_aws_ecr_login


def test_make_docker_aws_ecr_login_success():
    with patch("subprocess.run") as mock_run:
        make_docker_aws_ecr_login(dry_run=False)
        mock_run.assert_called_once_with(["make", "docker/aws_ecr_login"], check=True)


def test_make_docker_aws_ecr_login_failure():
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc_info:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "make docker/aws_ecr_login"
        )
        make_docker_aws_ecr_login(dry_run=False)
        assert "An error occurred:" in str(exc_info.value)
