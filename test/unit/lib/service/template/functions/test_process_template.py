import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from launch.lib.service.template.functions import process_template
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from test.conftest import fakeData_forLibServiceTemplateFunction as fakeData

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_dry_run(mock_secho, MockLaunchConfigTemplate, mock_paths, fakeData):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, fetch_fake_data(fakeData), dry_run=True)
    mock_secho.assert_called()
    MockLaunchConfigTemplate().assert_not_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_create_dirs(mock_secho, MockLaunchConfigTemplate, mock_paths, fakeData):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, fetch_fake_data(fakeData), dry_run=False)
    MockLaunchConfigTemplate().copy_additional_files.assert_called()
    MockLaunchConfigTemplate().properties_file.assert_called()
    MockLaunchConfigTemplate().templates.assert_called()
    MockLaunchConfigTemplate().template_properties.assert_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_skip_uuid(mock_secho, MockLaunchConfigTemplate, mock_paths, fakeData):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, fetch_fake_data(fakeData), skip_uuid=True, dry_run=False)
    MockLaunchConfigTemplate().uuid.assert_not_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_include_uuid(mock_secho, MockLaunchConfigTemplate, mock_paths, fakeData):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, fetch_fake_data(fakeData), skip_uuid=False, dry_run=False)
    MockLaunchConfigTemplate().uuid.assert_called()


def fetch_fake_data(fakeData):
    return fakeData("fakeData_forProcessTemplate.json")