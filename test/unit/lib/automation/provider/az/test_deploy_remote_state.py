import json
import subprocess
from pathlib import Path

import pytest

from launch.lib.automation.provider.az.functions import deploy_remote_state


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


def test_deploy_remote_state_all_parameters(mocker, fakedata):
    uuid_value = "uuid-test"
    naming_prefix = "test-prefix"
    target_environment = "prod"
    region = "us-west-2"
    instance = "instance1"
    expected_run_list = [
        "make",
        "NAME_PREFIX=test-prefix",
        "REGION=us-west-2",
        "ENVIRONMENT=prod",
        "ENV_INSTANCE=instance1",
        "CONTAINER_NAME=test_container",
        "RESOURCE_GROUP_NAME=test_resource_group",
        "STORAGE_ACCOUNT_NAME=test_storage_account",
        "terragrunt/remote_state/azure",
    ]

    mock_run = mocker.patch("launch.lib.automation.provider.az.functions.subprocess.run")
    mock_logger = mocker.patch("launch.lib.automation.provider.az.functions.logger.info")

    deploy_remote_state(
        uuid_value,
        naming_prefix,
        target_environment,
        region,
        instance,
        fakedata["provider_config"],
    )

    mock_run.assert_called_once_with(expected_run_list, check=True)
    mock_logger.assert_called()


def test_deploy_remote_state_minimal_parameters(mocker, fakedata):
    uuid_value = "uuid-test"
    naming_prefix = ""
    target_environment = ""
    region = ""
    instance = ""
    expected_run_list = [
        "make",
        "CONTAINER_NAME=test_container",
        "RESOURCE_GROUP_NAME=test_resource_group",
        "STORAGE_ACCOUNT_NAME=test_storage_account",
        "terragrunt/remote_state/azure",
    ]

    mock_run = mocker.patch("launch.lib.automation.provider.az.functions.subprocess.run")
    mock_logger = mocker.patch("launch.lib.automation.provider.az.functions.logger.info")

    deploy_remote_state(
        uuid_value,
        naming_prefix,
        target_environment,
        region,
        instance,
        fakedata["provider_config"],
    )

    mock_run.assert_called_once_with(expected_run_list, check=True)
    mock_logger.assert_called()


def test_deploy_remote_state_error_handling(mocker, fakedata):
    mocker.patch(
        "launch.lib.automation.provider.az.functions.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "make"),
    )

    with pytest.raises(RuntimeError) as excinfo:
        deploy_remote_state(
            "uuid-test",
            "test-prefix",
            "prod",
            "us-west-2",
            "instance1",
            fakedata["provider_config"],
        )

    assert "An error occurred:" in str(
        excinfo.value
    ), "Expected RuntimeError to be raised on subprocess.CalledProcessError"
