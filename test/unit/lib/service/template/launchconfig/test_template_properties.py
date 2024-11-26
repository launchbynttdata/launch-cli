import unittest
import pytest
import shutil
import os;
from unittest.mock import patch, MagicMock
from pathlib import Path

# Assuming the constants are defined somewhere
LAUNCHCONFIG_KEYS = MagicMock()
LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value = "template_properties"

from launch.lib.service.template.launchconfig import LaunchConfigTemplate

class TestTemplateProperties(unittest.TestCase):


    def test_template_properties_dry_run(self):
        with patch("click.secho") as mock_secho, patch("shutil.copy") as mock_copy,patch("os.makedirs") as mock_makedirs:

            launch_config = LaunchConfigTemplate(dry_run=True)
            value = {LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value: {"test": "test.yaml"}}
            current_path = Path("/current/path")
            dest_base = Path("/current")
            for name, file in value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value].items():
                file_path = Path(file).resolve()
                relative_path = current_path.joinpath(
                f"{LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value}/{name}.yaml"
                )
            
            launch_config.template_properties(value, current_path, dest_base)
            
            mock_secho.assert_called_once_with(
                f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                fg="yellow"
            )
            mock_makedirs.assert_not_called()
            mock_copy.assert_not_called()
            self.assertEqual(value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value]["test"], os.path.join("./path","template_properties","test.yaml"))


    def test_template_properties_success(self):
        with patch("click.secho") as mock_secho, patch("shutil.copy") as mock_copy,patch("os.makedirs") as mock_makedirs:

            launch_config = LaunchConfigTemplate(dry_run=False)
            value = {LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value: {"test": "test.yaml"}}
            current_path = Path("/current/path")
            dest_base = Path("/current")
            file = value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value].get("test")
            file_path = Path(file).resolve()
            
            launch_config.template_properties(value, current_path, dest_base)
            
            mock_secho.assert_not_called()
            mock_makedirs.assert_called_once_with(
                Path("/current/path/TEMPLATE_PROPERTIES"),
                exist_ok=True
            )
            mock_copy.assert_called_once_with(
                file_path, Path("/current/path/template_properties/test.yaml")
            )
            self.assertEqual(value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value]["test"], os.path.join("./path","template_properties","test.yaml"))