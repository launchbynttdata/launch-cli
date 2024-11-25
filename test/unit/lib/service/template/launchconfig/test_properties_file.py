import unittest
from unittest.mock import patch
from pathlib import Path
import os

from launch.lib.service.template.launchconfig import LAUNCHCONFIG_KEYS,LaunchConfigTemplate

class TestLaunchConfigTemplate(unittest.TestCase):

    def test_properties_file_dry_run(self):
        with patch("click.secho") as mock_secho, patch("shutil.copy") as mock_copy:
            launch_config = LaunchConfigTemplate(dry_run=True)
            value = {LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value: "test.properties"}
            file_path = Path(value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value]).resolve()
            current_path = Path("/current/path/test.properties")
            relative_path = current_path.joinpath(file_path.name)
            dest_base = Path("/current")

            launch_config.properties_file(value,current_path,dest_base)
            
            mock_secho.assert_called_once_with(
                f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                fg="yellow"
            )
            mock_copy.assert_not_called()
            self.assertEqual(value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value], os.path.join("./path","test.properties","terraform.tfvars"))

    def test_properties_file_success(self):
        with patch("click.secho") as mock_secho, patch("shutil.copy") as mock_copy:
            launch_config = LaunchConfigTemplate(dry_run=False)
            value = {LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value: "test.properties"}
            file_path = Path(value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value]).resolve()
            current_path = Path("/current/path")
            dest_base = Path("/current")
            
            launch_config.properties_file(value, current_path, dest_base)
            
            mock_secho.assert_not_called()
            mock_copy.assert_called_once_with(
                file_path, Path("/current/path/terraform.tfvars")
            )
            self.assertEqual(value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value], os.path.join("./path","terraform.tfvars"))

