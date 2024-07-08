import json
from pathlib import Path

import pytest

from launch.lib.automation.common.functions import traverse_with_callback
from launch.lib.automation.provider.az.functions import callback_deploy_remote_state


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


def test_value_is_dict(fakedata):
    value = {}
    result = callback_deploy_remote_state(fakedata["callback"]["key"], value)
    assert result is False


def test_uuid_with_all_kwargs(mocker, fakedata):
    mock_deploy = mocker.patch(
        "launch.lib.automation.provider.az.functions.deploy_remote_state"
    )
    kwargs = {
        "current_path": mocker.MagicMock(parts=["", "env", "instance"]),
        "naming_prefix": "prefix",
        "target_environment": "dev",
        "provider_config": {},
    }

    result = callback_deploy_remote_state(
        fakedata["callback"]["key"], fakedata["callback"]["value"], **kwargs
    )

    mock_deploy.assert_called_once_with(
        uuid_value=fakedata["callback"]["value"],
        naming_prefix="prefix",
        target_environment="dev",
        region="env",
        instance="instance",
        provider_config={},
    )
    assert result is True


def test_uuid_with_missing_kwargs(mocker, fakedata):
    mocker.patch("launch.lib.automation.provider.az.functions.logger")
    kwargs = {
        "current_path": mocker.MagicMock(parts=["", "env", "instance"]),
        "target_environment": "dev",
        "provider_config": {},
    }

    with pytest.raises(RuntimeError, match="Missing key in kwargs") as exc_info:
        callback_deploy_remote_state(
            fakedata["callback"]["key"], fakedata["callback"]["value"], **kwargs
        )
