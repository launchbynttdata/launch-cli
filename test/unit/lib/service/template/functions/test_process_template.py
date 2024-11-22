import pytest
from unittest.mock import MagicMock, patch
from launch.lib.service.template.functions import process_template
from pathlib import Path

from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

@pytest.fixture
def mock_paths():
    return Path('/mock/repo/base'), Path('/mock/dest/base')

@pytest.fixture
def mock_config():
    return {
        "dir1": {
            LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value: {
            "target1.txt": "source1.txt",
            "target2.txt": "source2.txt"
        },
            LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value: "properties",
            LAUNCHCONFIG_KEYS.TEMPLATES.value: {
            "template1": {"type1": "source_file_1.yaml", "type2": "source_file_2.yaml"},
            "template2": {"type1": "source_file_3.yaml"}
        }
        },
        "dir2": "file.txt"
    }

def test_process_template_success(mock_paths, mock_config):
    repo_base, dest_base = mock_paths
    
    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch("shutil.copy") as mock_copy, \
         patch('launch.lib.service.template.launchconfig.LaunchConfigTemplate') as MockLaunchConfigTemplate, \
         patch('click.secho') as mock_secho:

        mock_instance = MockLaunchConfigTemplate.return_value
        mock_instance.copy_additional_files = MagicMock()
        mock_instance.properties_file = MagicMock()
        mock_instance.templates = MagicMock()

        result = process_template(repo_base, dest_base, mock_config, dry_run=False)

        assert result == mock_config
        mock_mkdir.assert_called()
        assert mock_copy.call_count == 6
        mock_secho.assert_not_called()

def test_process_template_dry_run(mock_paths, mock_config):
    repo_base, dest_base = mock_paths

    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('launch.lib.service.template.launchconfig.LaunchConfigTemplate') as MockLaunchConfigTemplate, \
         patch('click.secho') as mock_secho:

        result = process_template(repo_base, dest_base, mock_config, dry_run=True)

        assert result == mock_config
        mock_mkdir.assert_not_called()
        mock_secho.assert_called()
        assert mock_secho.call_count == 11

def test_process_template_empty_config(mock_paths):
    repo_base, dest_base = mock_paths

    result = process_template(repo_base, dest_base, {}, dry_run=False)

    assert result == {}

def test_process_template_invalid_key(mock_paths):
    repo_base, dest_base = mock_paths
    invalid_config = {"invalid_key": "some_value"}

    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('launch.lib.service.template.launchconfig.LaunchConfigTemplate') as MockLaunchConfigTemplate:

        result = process_template(repo_base, dest_base, invalid_config, dry_run=False)

        assert result == invalid_config
        mock_mkdir.assert_not_called()

def test_process_template_skip_uuid(mock_paths, mock_config):
    repo_base, dest_base = mock_paths

    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('launch.lib.service.template.launchconfig.LaunchConfigTemplate') as MockLaunchConfigTemplate, \
         patch('click.secho') as mock_secho:

        mock_instance = MockLaunchConfigTemplate.return_value
        mock_instance.uuid = MagicMock()

        result = process_template(repo_base, dest_base, mock_config, skip_uuid=True)

        assert result == mock_config
        mock_instance.uuid.assert_not_called()
