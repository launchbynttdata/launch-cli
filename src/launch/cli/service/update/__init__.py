import logging
from pathlib import Path
from typing import IO, Any

import click
from git import Repo

from launch.config.common import PLATFORM_SRC_DIR_PATH
from launch.config.github import GITHUB_ORG_NAME
from launch.config.launchconfig import SERVICE_MAIN_BRANCH, SERVICE_REMOTE_BRANCH
from launch.lib.github.repo import repo_exist
from launch.lib.local_repo.repo import checkout_branch, clone_repository
from launch.lib.service.common import determine_existing_uuid
from launch.lib.service.functions import common_service_workflow, prepare_service

logger = logging.getLogger(__name__)


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
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
def update(
    name: str,
    in_file: IO[Any],
    git_message: str,
    uuid: bool,
    skip_git: bool,
    skip_commit: bool,
    skip_sync: bool,
    dry_run: bool,
):
    """
    Updates a service based on the latest supplied inputs and any changes from the skeleton. This command will
    clone the repository, update the service with the latest inputs, and push the changes to the remote repository.

    Args:
        name (str): The name of the service to be updated.
        in_file (IO[Any]): The input file to be used to update the service.
        git_message (str): The git commit message to use when creating a commit.
        uuid (bool): If set, it will generate a new UUID to be used in skeleton files.
        skip_git (bool): If set, it will ignore cloning and checking out the git repository.
        skip_commit (bool): If set, it will skip commiting the local changes.
        skip_sync (bool): If set, it will skip syncing the template files and only update the properties files and directories.
        dry_run (bool): If set, it will not make any changes, but will log what it would
    """

    if skip_git:
        if not f"{Path.cwd()}/{name}":
            click.secho(f"Error: Path {service_path} does not exist.", fg="red")
            return

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

    if not skip_git:
        if Path(service_path).exists():
            click.secho(
                f"Directory with the name {service_path} already exists. Skipping cloning the repository.",
                fg="red",
            )
            repository = Repo(service_path)
        else:
            if dry_run:
                click.secho(
                    f"[DRYRUN] Would have cloned a repo into a dir with the following, {name=} {SERVICE_REMOTE_BRANCH=}",
                    fg="yellow",
                )
            else:
                repository = clone_repository(
                    repository_url=remote_repo.clone_url,
                    target=name,
                    branch=SERVICE_MAIN_BRANCH,
                )
            checkout_branch(
                repository=repository,
                target_branch=SERVICE_REMOTE_BRANCH,
                dry_run=dry_run,
            )
    else:
        repository = Repo(service_path)

    input_data[PLATFORM_SRC_DIR_PATH] = determine_existing_uuid(
        input_data=input_data[PLATFORM_SRC_DIR_PATH], path=service_path
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
