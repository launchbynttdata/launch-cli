import logging
from pathlib import Path
from typing import IO, Any

import click
from git import Repo

from launch.config.common import PLATFORM_SRC_DIR_PATH
from launch.config.github import GITHUB_ORG_NAME
from launch.config.launchconfig import SERVICE_MAIN_BRANCH, SERVICE_REMOTE_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.github.repo import repo_exist
from launch.lib.local_repo.repo import checkout_branch, clone_repository
from launch.lib.service.common import determine_existing_uuid
from launch.lib.service.functions import common_service_workflow, prepare_service

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--name", default=Path.cwd().name, help="Name of the service to be updated."
)
@click.option(
    "--in-file",
    required=None,
    type=click.File("r"),
    help=f"(Optional) Inputs to be used to update the repo. Defaults to looking for the {LAUNCHCONFIG_NAME} in current directory.",
)
@click.option(
    "--git-message",
    default="bot: launch-cli service update commit",
    help="(Optional) The git commit message to use when creating a commit. Defaults to 'bot: launch service update commit'.",
)
@click.option(
    "--uuid",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will generate a new UUID to be used in skeleton files.",
)
@click.option(
    "--clone",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will clone the repository and perform the update.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will ignore cloning and checking out the git repository.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will skip commiting the local changes.",
)
@click.option(
    "--skip-sync",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will skip syncing the template files and only update the properties files and directories.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="(Optional) Override safeguards.",
)
def update(
    name: str,
    in_file: IO[Any],
    git_message: str,
    uuid: bool,
    clone: bool,
    skip_git: bool,
    skip_commit: bool,
    skip_sync: bool,
    dry_run: bool,
    force: bool,
):
    """
    Updates a service based on the latest supplied inputs and any changes from the skeleton. This command will
    clone the repository, update the service with the latest inputs, and push the changes to the remote repository.

    Args:
        in_file (IO[Any]): The input file to be used to update the service.
        git_message (str, Optional): The git commit message to use when creating a commit.
        uuid (bool): If set, it will generate a new UUID to be used in skeleton files.
        clone (bool): If set, it will clone the repository and perform the update.
        skip_git (bool): If set, it will ignore cloning and checking out the git repository.
        skip_commit (bool): If set, it will skip commiting the local changes.
        skip_sync (bool): If set, it will skip syncing the template files and only update the properties files and directories.
        dry_run (bool): If set, it will not make any changes, but will log what it would.
        force (bool): If set, it will override safeguards.
    """

    input_data, service_path, repository, g = prepare_service(
        name=name,
        in_file=in_file,
        dry_run=dry_run,
    )

    if not repo_exist(name=f"{GITHUB_ORG_NAME}/{name}", g=g):
        click.secho(
            "Repo does not exist remotely. Please use launch service create to create a new service.",
            fg="red",
        )
        return

    if dry_run:
        click.secho(
            f"[DRYRUN] Would have gotten repo object: {GITHUB_ORG_NAME}/{name}",
            fg="yellow",
        )
    else:
        remote_repo = g.get_repo(f"{GITHUB_ORG_NAME}/{name}")

    if not skip_git and clone:
        if Path(service_path).exists():
            click.secho(
                f"Directory with the name {service_path} already exists. Skipping cloning the repository.",
                fg="red",
            )
            repository = Repo(service_path)
        else:
            repository = clone_repository(
                repository_url=remote_repo.clone_url,
                target=service_path,
                branch=SERVICE_MAIN_BRANCH,
                dry_run=dry_run,
            )
            checkout_branch(
                repository=repository,
                target_branch=SERVICE_REMOTE_BRANCH,
                dry_run=dry_run,
            )
    else:
        repository = Repo(service_path)

    input_data[PLATFORM_SRC_DIR_PATH] = determine_existing_uuid(
        input_data=input_data[PLATFORM_SRC_DIR_PATH],
        path=service_path,
        force=force,
    )

    common_service_workflow(
        service_path=service_path,
        repository=repository,
        input_data=input_data,
        git_message=git_message,
        uuid=uuid,
        skip_sync=skip_sync,
        skip_git=skip_git,
        skip_commit=skip_commit,
        dry_run=dry_run,
    )
