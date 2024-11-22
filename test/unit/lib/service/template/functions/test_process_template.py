import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from launch.lib.service.template.functions import process_template
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

@pytest.fixture
def mock_paths(tmp_path):
    repo_base = tmp_path / "repo_base"
    dest_base = tmp_path / "dest_base"
    repo_base.mkdir()
    dest_base.mkdir()
    return repo_base, dest_base

@pytest.fixture
def mock_config():
    return {
        "dir1": {
            "dir2": {
                LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value: {},
                LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value: {},
                LAUNCHCONFIG_KEYS.TEMPLATES.value: {},
                LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value: {},
            }
        }
    }

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_dry_run(mock_secho, MockLaunchConfigTemplate, mock_paths, mock_config):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, mock_config, dry_run=True)
    mock_secho.assert_called()
    MockLaunchConfigTemplate().assert_not_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_create_dirs(mock_secho, MockLaunchConfigTemplate, mock_paths, mock_config):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, mock_config, dry_run=False)
    MockLaunchConfigTemplate().copy_additional_files.assert_called()
    MockLaunchConfigTemplate().properties_file.assert_called()
    MockLaunchConfigTemplate().templates.assert_called()
    MockLaunchConfigTemplate().template_properties.assert_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_skip_uuid(mock_secho, MockLaunchConfigTemplate, mock_paths, mock_config):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, mock_config, skip_uuid=True, dry_run=False)
    MockLaunchConfigTemplate().uuid.assert_not_called()

@patch("launch.lib.service.template.functions.LaunchConfigTemplate")
@patch("launch.lib.service.template.functions.click.secho")
def test_process_template_include_uuid(mock_secho, MockLaunchConfigTemplate, mock_paths, mock_config):
    repo_base, dest_base = mock_paths
    process_template(repo_base, dest_base, mock_config, skip_uuid=False, dry_run=False)
    MockLaunchConfigTemplate().uuid.assert_called()