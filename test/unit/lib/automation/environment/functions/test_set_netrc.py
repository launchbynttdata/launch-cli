import importlib
import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open

import pytest
from faker import Faker

from launch.lib.automation.environment import functions

fake = Faker()


@pytest.fixture
def set_pipeline(mocker):
    mocker.patch.object(functions, "IS_PIPELINE", True)
    yield


@pytest.fixture
def set_no_pipeline(mocker):
    mocker.patch.object(functions, "IS_PIPELINE", False)
    yield


@pytest.fixture
def no_netrc():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir).joinpath(".netrc")


@pytest.fixture
def existing_netrc():
    with tempfile.TemporaryDirectory() as temp_dir:
        netrc_path = Path(temp_dir).joinpath(".netrc")
        netrc_path.write_text(
            "machine example.com\nlogin username\npassword password123\n"
        )
        yield netrc_path


def test_pipeline_environment_variable_skips_netrc(mocker, no_netrc, set_no_pipeline):
    click_echo = mocker.patch("click.echo")

    functions.set_netrc("password123", netrc_path=no_netrc, dry_run=False)
    click_echo.assert_called_once_with(
        f"Not running in a pipeline, skipping setting {no_netrc} variables."
    )


def test_set_netrc_success(no_netrc, set_pipeline):
    fake_username = fake.user_name()
    fake_password = fake.password()
    fake_domain = fake.domain_name()

    """A successful netrc write and chmod."""
    functions.set_netrc(
        password=fake_password,
        machine=fake_domain,
        login=fake_username,
        netrc_path=no_netrc,
        dry_run=False,
    )

    assert no_netrc.exists()
    netrc_contents = no_netrc.read_text()
    assert (
        f"machine {fake_domain}\nlogin {fake_username}\npassword {fake_password}\n"
        in netrc_contents
    )
    assert no_netrc.stat().st_mode & 0o777 == 0o600


def test_set_netrc_exception_during_write(mocker, no_netrc, set_pipeline):
    """Simulates an unsuccessful write."""
    mocker.patch("builtins.open", side_effect=IOError("File write error"))

    with pytest.raises(RuntimeError, match="An error occurred"):
        functions.set_netrc(
            "password123",
            "example.com",
            "username",
            netrc_path=no_netrc,
            dry_run=False,
        )


def test_set_netrc_exception_during_chmod(mocker, no_netrc, set_pipeline):
    """Simulates a successful write but unsuccessful chmod."""
    mocker.patch("os.chmod", side_effect=OSError("Permission error"))

    with pytest.raises(RuntimeError, match="An error occurred"):
        functions.set_netrc(
            "password123",
            "example.com",
            "username",
            netrc_path=no_netrc,
            dry_run=False,
        )
