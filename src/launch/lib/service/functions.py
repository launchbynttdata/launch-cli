import json
import logging
import shutil
from pathlib import Path

import click
from git import Repo

from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.service import SERVICE_REMOTE_BRANCH
from launch.lib.github.auth import get_github_instance
from launch.lib.local_repo.repo import clone_repository, push_branch
from launch.lib.service.common import input_data_validation, write_text
from launch.lib.service.template.functions import copy_template_files, process_template

logger = logging.getLogger(__name__)


def prepare_service(
    name: str,
    in_file: Path,
    dry_run: bool,
) -> None:
    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be created", fg="yellow"
        )

    service_path = f"{Path.cwd()}/{name}"
    input_data = json.load(in_file)
    input_data = input_data_validation(input_data)
    repository = None

    g = get_github_instance()

    # Ensure we have a fresh build directory for our build files
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have removed the following directory: {BUILD_TEMP_DIR_PATH=}",
                fg="yellow",
            )
        else:
            shutil.rmtree(BUILD_TEMP_DIR_PATH)
    except FileNotFoundError:
        logger.info(
            f"Directory not found when trying to delete: {BUILD_TEMP_DIR_PATH=}"
        )

    return input_data, service_path, repository, g


def common_service_workflow(
    service_path: str,
    repository: Repo,
    input_data: dict,
    git_message: str,
    uuid: bool,
    skip_sync: bool,
    skip_git: bool,
    skip_commit: bool,
    dry_run: bool,
) -> None:
    # Clone the skeleton repository. We need this to copy dir structure and any global repo files.
    # This is a temporary directory that will be deleted after the service is created.
    if dry_run and not skip_git:
        url = input_data["skeleton"]["url"]
        tag = input_data["skeleton"]["tag"]
        click.secho(
            f"[DRYRUN] Would have cloned a repo into a dir with the following, {url=} {BUILD_TEMP_DIR_PATH=} {tag}",
            fg="yellow",
        )
    elif not skip_git:
        clone_repository(
            repository_url=input_data["skeleton"]["url"],
            target=f"{BUILD_TEMP_DIR_PATH}/skeleton",
            branch=input_data["skeleton"]["tag"],
        )

    # Copy all the files from the skeleton repo to the service directory unless flag is set.
    if not skip_sync:
        copy_template_files(
            src_dir=Path(f"{BUILD_TEMP_DIR_PATH}/skeleton"),
            target_dir=Path(service_path),
            exclude_dir=PLATFORM_SRC_DIR_PATH,
            dry_run=dry_run,
        )

    # Process the template files. This is the main logic that loops over the template and
    # creates the directories and files in the service directory.
    input_data["platform"] = process_template(
        src_base=Path(f"{BUILD_TEMP_DIR_PATH}/skeleton"),
        dest_base=Path(service_path),
        config={PLATFORM_SRC_DIR_PATH: input_data["platform"]},
        skip_uuid=not uuid,
        dry_run=dry_run,
    )

    # Write the .launch_config file
    write_text(
        data=input_data,
        path=Path(f"{service_path}/.launch_config"),
        dry_run=dry_run,
    )

    # Push the branch to the remote repository unless the flag is set.
    if not skip_git and not skip_commit:
        push_branch(
            repository=repository,
            branch=SERVICE_REMOTE_BRANCH,
            commit_msg=git_message,
            dry_run=dry_run,
        )

    if dry_run:
        click.secho(
            f"[DRYRUN] .launch_config: {input_data}",
            fg="yellow",
        )
