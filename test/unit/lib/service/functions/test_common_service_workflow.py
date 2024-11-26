from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.launchconfig import SERVICE_REMOTE_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.service.functions import common_service_workflow


def setup_patches(mocker):
    patches = {
        "extract_repo_name_from_url": mocker.patch(
            "launch.lib.service.functions.extract_repo_name_from_url",
            return_value="repo_name",
        ),
        "clone_repository": mocker.patch(
            "launch.lib.service.functions.clone_repository"
        ),
        "copy_template_files": mocker.patch(
            "launch.lib.service.functions.copy_template_files"
        ),
        "process_template": mocker.patch(
            "launch.lib.service.functions.process_template",
            return_value={PLATFORM_SRC_DIR_PATH: "processed_path"},
        ),
        "write_text": mocker.patch("launch.lib.service.functions.write_text"),
        "push_branch": mocker.patch("launch.lib.service.functions.push_branch"),
        "secho": mocker.patch("click.secho"),
    }
    return patches


def setup_data(fakedata):
    data = {
        "service_path": "service_path",
        "repository": MagicMock(),
        "input_data": fakedata["workflow"],
        "git_message": "commit message",
        "skip_uuid": False,
        "skip_sync": False,
        "skip_git": False,
        "skip_commit": False,
        "dry_run": False,
    }
    return data


def test_common_service_workflow(mocker, fakedata):
    patches = setup_patches(mocker)
    data = setup_data(fakedata)

    try:
        common_service_workflow(
            data["service_path"],
            data["repository"],
            data["input_data"],
            data["git_message"],
            data["skip_uuid"],
            data["skip_sync"],
            data["skip_git"],
            data["skip_commit"],
            data["dry_run"],
        )
    except KeyError as e:
        assert str(e) == "'platform'"

    patches["extract_repo_name_from_url"].assert_called()
    patches["clone_repository"].assert_any_call(
        repository_url="skeleton_url",
        target=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        branch="skeleton_tag",
        dry_run=data["dry_run"],
    )
    patches["clone_repository"].assert_any_call(
        repository_url="app_url",
        target=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        branch="app_tag",
        dry_run=data["dry_run"],
    )
    patches["copy_template_files"].assert_any_call(
        src_dir=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        target_dir=Path(data["service_path"]),
        dry_run=data["dry_run"],
    )
    patches["copy_template_files"].assert_any_call(
        src_dir=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        target_dir=Path(data["service_path"]),
        not_platform=True,
        dry_run=data["dry_run"],
    )
    patches["process_template"].assert_called_with(
        repo_base=Path.cwd(),
        dest_base=Path(data["service_path"]),
        config={PLATFORM_SRC_DIR_PATH: "platform_src_path"},
        skip_uuid=data["skip_uuid"],
        dry_run=data["dry_run"],
    )
    patches["write_text"].assert_called_with(
        data=data["input_data"],
        path=Path(f"{data['service_path']}/{LAUNCHCONFIG_NAME}"),
        dry_run=data["dry_run"],
    )
    patches["push_branch"].assert_called_with(
        repository=data["repository"],
        branch=SERVICE_REMOTE_BRANCH,
        commit_msg=data["git_message"],
        dry_run=data["dry_run"],
    )
