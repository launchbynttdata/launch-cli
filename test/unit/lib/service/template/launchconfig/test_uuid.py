import pytest
from unittest.mock import patch
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from launch.lib.service.template.launchconfig import LaunchConfigTemplate


@pytest.fixture

def test_uuid_added_when_missing(fakedata):
    value = {}
    with patch('uuid.uuid4', return_value=fakedata[LAUNCHCONFIG_KEYS.UUID.value]):
        LaunchConfigTemplate("false").uuid(value)
        assert LAUNCHCONFIG_KEYS.UUID.value in value
        assert value[LAUNCHCONFIG_KEYS.UUID.value] == fakedata[LAUNCHCONFIG_KEYS.UUID.value][-6:]

def test_uuid_unchanged_when_present(fakedata):
    value = {LAUNCHCONFIG_KEYS.UUID.value: fakedata["existing_uuid"]}
    LaunchConfigTemplate("false").uuid(value)
    assert value[LAUNCHCONFIG_KEYS.UUID.value] == fakedata["existing_uuid"]

