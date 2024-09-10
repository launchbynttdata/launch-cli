import json
import logging
import shutil
from pathlib import Path
from typing import IO, Any

import click
from git import Repo

from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.launchconfig import SERVICE_REMOTE_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.common.utilities import extract_repo_name_from_url
from launch.lib.github.auth import get_github_instance
from launch.lib.local_repo.repo import clone_repository, push_branch
from launch.lib.service.common import input_data_validation, write_text
from launch.lib.service.template.functions import copy_template_files, process_template

logger = logging.getLogger(__name__)


def prepare_service(
    name: str,
    in_file: IO[Any] = None,
    dry_run: bool = True,
) -> None:
    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be created", fg="yellow"
        )

    if in_file:
        input_data = json.loads(in_file.read())
        service_path = f"{Path.cwd()}/{name}"
    elif Path(LAUNCHCONFIG_NAME).exists():
        input_data = json.loads(Path(LAUNCHCONFIG_NAME).read_text())
        service_path = f"{Path.cwd()}"
    else:
        click.secho(
            f"No --in-file supplied and could not find {LAUNCHCONFIG_NAME} in the current directory. Exiting...",
            fg="red",
        )
        quit()

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
            f"Directory not found when trying to delete to clean the workspace: {BUILD_TEMP_DIR_PATH=}"
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
    skeleton_path = Path(
        f"{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(input_data['skeleton']['url'])}"
    )
    if "application" in input_data["sources"]:
        application_path = Path(
            f"{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(input_data['sources']['application']['url'])}"
        )

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
            target=skeleton_path,
            branch=input_data["skeleton"]["tag"],
            dry_run=dry_run,
        )
        if "application" in input_data["sources"]:
            clone_repository(
                repository_url=input_data["sources"]["application"]["url"],
                target=application_path,
                branch=input_data["sources"]["application"]["tag"],
                dry_run=dry_run,
            )

    # Copy all the files from the skeleton repo to the service directory unless flag is set.
    if not skip_sync:
        copy_template_files(
            src_dir=skeleton_path,
            target_dir=Path(service_path),
            dry_run=dry_run,
        )
        if "application" in input_data["sources"]:
            copy_template_files(
                src_dir=application_path,
                target_dir=Path(service_path),
                not_platform=True,
                dry_run=dry_run,
            )

    # Process the template files. This is the main logic that loops over the template and
    # creates the directories and files in the service directory.
    input_data[PLATFORM_SRC_DIR_PATH] = process_template(
        repo_base=Path.cwd(),
        dest_base=Path(service_path),
        config={PLATFORM_SRC_DIR_PATH: input_data[PLATFORM_SRC_DIR_PATH]},
        skip_uuid=not uuid,
        dry_run=dry_run,
    )[PLATFORM_SRC_DIR_PATH]

    # Write the .launch_config file
    write_text(
        data=input_data,
        path=Path(f"{service_path}/{LAUNCHCONFIG_NAME}"),
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
            f"[DRYRUN] {LAUNCHCONFIG_NAME}: {input_data}",
            fg="yellow",
        )
