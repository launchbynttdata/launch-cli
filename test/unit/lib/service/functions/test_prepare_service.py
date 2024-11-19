import json
from pathlib import Path

import pytest

from launch.config.common import BUILD_TEMP_DIR_PATH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.service.functions import prepare_service


def test_prepare_service(mocker):
    # Mock dependencies
    mock_get_github_instance = mocker.patch(
        "launch.lib.service.functions.get_github_instance"
    )
    mock_path_exists = mocker.patch("launch.lib.service.functions.Path.exists")
    mock_path_read_text = mocker.patch("launch.lib.service.functions.Path.read_text")
    mock_click_secho = mocker.patch("launch.lib.service.functions.click.secho")

    # Test dry run with in_file
    mock_file = mocker.mock_open(read_data=json.dumps({"key": "value"}))
    mocker.patch("builtins.open", mock_file)
    mocker.patch("json.load", return_value={"key": "value"})
    with open("mock_file") as f:
        input_data, service_path, repository, g = prepare_service(
            name="test_service", in_file=f, dry_run=True
        )
    assert input_data == {
        "key": "value",
        "skeleton": {
            "url": "https://github.com/launchbynttdata/lcaf-template-terragrunt.git",
            "tag": "main",
        },
    }
    assert service_path == f"{Path.cwd()}/test_service"
    assert repository is None
    assert g == mock_get_github_instance.return_value
    mock_click_secho.assert_called_with(
        f"[DRYRUN] Would have removed the following directory: {BUILD_TEMP_DIR_PATH=}",
        fg="yellow",
    )

    # Test dry run without in_file but with LAUNCHCONFIG_NAME
    mock_path_exists.return_value = True
    mock_path_read_text.return_value = json.dumps({"key": "value"})
    input_data, service_path, repository, g = prepare_service(
        name="test_service", in_file=None, dry_run=True
    )
    assert input_data == {
        "key": "value",
        "skeleton": {
            "url": "https://github.com/launchbynttdata/lcaf-template-terragrunt.git",
            "tag": "main",
        },
    }
    assert service_path == f"{Path.cwd()}"
    assert repository is None
    assert g == mock_get_github_instance.return_value
    mock_click_secho.assert_called_with(
        f"[DRYRUN] Would have removed the following directory: {BUILD_TEMP_DIR_PATH=}",
        fg="yellow",
    )

    # Test no in_file and no LAUNCHCONFIG_NAME
    mock_path_exists.return_value = False
    with pytest.raises(SystemExit):
        prepare_service(name="test_service", in_file=None, dry_run=True)
    mock_click_secho.assert_called_with(
        f"No --in-file supplied and could not find {LAUNCHCONFIG_NAME} in the current directory. Exiting...",
        fg="red",
    )
