import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from launch.lib.service.template.launchconfig import LaunchConfigTemplate


def test_templates(mocker, fakedata):
    mocker.patch("os.makedirs")
    mocker.patch("shutil.copy")

    value = {"templates": fakedata["templates"]}
    current_path = Path("/absolute/path/to/current")
    dest_base = Path("/absolute/path/to/")

    launch_config = LaunchConfigTemplate(dry_run=False)
    launch_config.templates(value, current_path, dest_base)

    os.makedirs.assert_called_with(
        current_path.joinpath("templates/my_template"), exist_ok=True
    )

    assert value["templates"]["my_template"]["readme"] == (
        "./current/templates/my_template/readme.yaml"
    )
    assert value["templates"]["my_template"]["config"] == (
        "./current/templates/my_template/config.yaml"
    )

    assert shutil.copy.call_count == 2
