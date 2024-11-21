from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.launchconfig import SERVICE_REMOTE_BRANCH
from launch.lib.service.functions import common_service_workflow


def test_common_service_workflow(mocker, fakedata):
    LAUNCHCONFIG_NAME = mocker.patch(
        "launch.constants.launchconfig.LAUNCHCONFIG_NAME", ".launch_config"
    )
    extract_repo_name_from_url = mocker.patch(
        "launch.lib.service.functions.extract_repo_name_from_url",
        return_value="repo_name",
    )
    clone_repository = mocker.patch("launch.lib.service.functions.clone_repository")
    copy_template_files = mocker.patch(
        "launch.lib.service.functions.copy_template_files"
    )
    process_template = mocker.patch(
        "launch.lib.service.functions.process_template",
        return_value={PLATFORM_SRC_DIR_PATH: "processed_path"},
    )
    write_text = mocker.patch("launch.lib.service.functions.write_text")
    push_branch = mocker.patch("launch.lib.service.functions.push_branch")
    mocker.patch("click.secho")

    service_path = "service_path"
    repository = MagicMock()
    input_data = fakedata["workflow"]
    git_message = "commit message"
    skip_uuid = False
    skip_sync = False
    skip_git = False
    skip_commit = False
    dry_run = False

    try:
        common_service_workflow(
            service_path,
            repository,
            input_data,
            git_message,
            skip_uuid,
            skip_sync,
            skip_git,
            skip_commit,
            dry_run,
        )
    except KeyError as e:
        assert str(e) == "'platform'"

    extract_repo_name_from_url.assert_called()
    clone_repository.assert_any_call(
        repository_url="skeleton_url",
        target=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        branch="skeleton_tag",
        dry_run=dry_run,
    )
    clone_repository.assert_any_call(
        repository_url="app_url",
        target=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        branch="app_tag",
        dry_run=dry_run,
    )
    copy_template_files.assert_any_call(
        src_dir=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        target_dir=Path(service_path),
        dry_run=dry_run,
    )
    copy_template_files.assert_any_call(
        src_dir=Path(f"{BUILD_TEMP_DIR_PATH}/repo_name"),
        target_dir=Path(service_path),
        not_platform=True,
        dry_run=dry_run,
    )
    process_template.assert_called_with(
        repo_base=Path.cwd(),
        dest_base=Path(service_path),
        config={PLATFORM_SRC_DIR_PATH: "platform_src_path"},
        skip_uuid=skip_uuid,
        dry_run=dry_run,
    )
    write_text.assert_called_with(
        data=input_data,
        path=Path(f"{service_path}/{LAUNCHCONFIG_NAME}"),
        dry_run=dry_run,
    )
    push_branch.assert_called_with(
        repository=repository,
        branch=SERVICE_REMOTE_BRANCH,
        commit_msg=git_message,
        dry_run=dry_run,
    )
