import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import click

from launch.lib.automation.terragrunt.functions import find_app_templates

class TestFindAppTemplates(unittest.TestCase):

    def test_find_app_templates(self):
        with patch("os.walk") as mock_os_walk, patch("launch.lib.automation.terragrunt.functions.process_app_templates") as mock_process_app_templates:
            context = MagicMock(spec=click.Context)
            base_dir = Path("/base/dir")
            template_dir = Path("/template/dir")
            aws_profile = "test-profile"
            aws_region = "us-west-2"
            dry_run = True

            mock_os_walk.return_value = [
                ("/base/dir", ["template_properties"], ["file1", "file2"]),
                ("/base/dir/subdir", [], ["file3"]),
            ]

            find_app_templates(context, base_dir, template_dir, aws_profile, aws_region, dry_run)

            mock_process_app_templates.assert_called_once_with(
                context=context,
                instance_path="/base/dir",
                properties_path=Path("/base/dir/template_properties"),
                template_dir=template_dir,
                aws_profile=aws_profile,
                aws_region=aws_region,
                dry_run=dry_run,
            )