import json
import logging
from pathlib import Path
from typing import IO, Any

import click

from launch.cli.github.access.commands import set_default
from launch.config.common import PLATFORM_SRC_DIR_PATH
from launch.config.github import GITHUB_ORG_NAME
from launch.config.launchconfig import SERVICE_MAIN_BRANCH, SERVICE_REMOTE_BRANCH
from launch.lib.github.repo import create_repository, repo_exist
from launch.lib.local_repo.repo import checkout_branch, clone_repository
from launch.lib.service.common import input_data_validation, write_text
from launch.lib.service.functions import common_service_workflow, prepare_service
from launch.lib.service.template.functions import process_template

logger = logging.getLogger(__name__)


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--description",
    default="Service created with launch-cli.",
    help="(Optional) A short description of the repository.",
)
@click.option(
    "--public",
    is_flag=True,
    default=False,
    help="(Optional) The visibility of the repository.",
)
@click.option(
    "--visibility",
    default="private",
    help="(Optional) The visibility of the repository. Can be one of: public, private.",
)
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--git-message",
    default="bot: launch-cli service create initial commit",
    help="(Optional) The git commit message to use when creating a commit. Defaults to 'Initial commit'.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will skip all actions with git. Overrides --skip-commit.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will skip commiting the local changes.",
)
@click.option(
    "--skip-uuid",
    is_flag=True,
    default=False,
    help="(Optional) If set, it will not generate a UUID to be used in skeleton files.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do.",
)
@click.pass_context
# TODO: Optimize this function and logic
# Ticket: 1633
def create(
    context: click.Context,
    name: str,
    description: str,
    public: bool,
    visibility: str,
    in_file: IO[Any],
    git_message: str,
    skip_git: bool,
    skip_commit: bool,
    skip_uuid: bool,
    dry_run: bool,
):
    """
    Creates a new service.  This command will create a new repository in the organization, clone the skeleton repository,
    create a directory structure based on the inputs and copy the necessary files to the new repository. It will then push
    the changes to the remote repository.

    Args:
        name (str): The name of the service to be created.
        description (str): A short description of the repository.
        public (bool): The visibility of the repository.
        visibility (str): The visibility of the repository. Can be one of: public, private.
        in_file (IO[Any]): Inputs to be used with the skeleton during creation.
        git_message (str): The git commit message to use when creating a commit. Defaults to 'Initial commit'.
        skip_git (bool): If set, it will skip all actions with git. Overrides --skip-commit.
        skip_commit (bool): If set, it will skip commiting the local changes.
        skip_uuid (bool): If set, it will not generate a UUID to be used in skeleton files.
        dry_run (bool): Perform a dry run that reports on what it would do, but does not create webhooks.
    """

    input_data, service_path, repository, g = prepare_service(
        name=name,
        in_file=in_file,
        dry_run=dry_run,
    )

    # Check if the repository already exists. If it does, we do not want to try and create it.
    if repo_exist(name=f"{GITHUB_ORG_NAME}/{name}", g=g) and not skip_git:
        click.secho(
            "Repo already exists remotely. Please use launch service update, to update a service.",
            fg="red",
        )
        return
    if Path(service_path).exists():
        click.secho(
            f"Directory with the name {service_path} already exists. Please remove this directory or use a different name.",
            fg="red",
        )
        return

    # Create the repository
    if not skip_git:
        service_repo = create_repository(
            g=g,
            organization=GITHUB_ORG_NAME,
            name=name,
            description=description,
            public=public,
            visibility=visibility,
            dry_run=dry_run,
        )
    # Set the default access permissions on the repository
    if not skip_git:
        context.invoke(
            set_default,
            organization=GITHUB_ORG_NAME,
            repository_name=name,
            dry_run=dry_run,
        )

    # Clone the repository. When we create the repository, it does not create a local repository.
    # thus we need to clone it to create a local repository.
    if not skip_git:
        if dry_run and not skip_git:
            click.secho(
                f"[DRYRUN] Would have cloned a repo into a dir with the following, {name=} {SERVICE_MAIN_BRANCH=}",
                fg="yellow",
            )

        else:
            repository = clone_repository(
                repository_url=service_repo.clone_url,
                target=name,
                branch=SERVICE_MAIN_BRANCH,
                dry_run=dry_run,
            )
    else:
        needs_create = not Path(service_path).exists()
        if needs_create:
            if dry_run:
                click.secho(
                    f"[DRYRUN] Would have created dir, {service_path=}",
                    fg="yellow",
                )
            else:
                Path(service_path).mkdir(exist_ok=False)
        is_service_path_git_repo = (
            Path(service_path).joinpath(".git").exists()
            and Path(service_path).joinpath(".git").is_dir()
        )
        if is_service_path_git_repo:
            click.secho(
                f"{service_path} appears to be a git repository! You will need to add, commit, and push these files manually.",
                fg="yellow",
            )
        else:
            if needs_create:
                click.secho(
                    f"{service_path} was created, but has not yet been initialized as a git repository. You will need to initialize it.",
                    fg="yellow",
                )
            else:
                click.secho(
                    f"{service_path} already existed, but has not yet been initialized as a git repository. You will need to initialize it.",
                    fg="yellow",
                )
    # Checkout the branch
    if not skip_git:
        checkout_branch(
            repository=repository,
            target_branch=SERVICE_REMOTE_BRANCH,
            new_branch=True,
            dry_run=dry_run,
        )

    common_service_workflow(
        service_path=service_path,
        repository=repository,
        input_data=input_data,
        git_message=git_message,
        uuid=not skip_uuid,
        skip_sync=False,
        skip_git=skip_git,
        skip_commit=skip_commit,
        dry_run=dry_run,
    )


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def create_dir_offline(
    name: str,
    in_file: IO[Any],
    dry_run: bool,
):
    """Creates a new service without any Git interactions."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")
        # TODO: add a dry run for the create command
        return

    service_path = f"{Path.cwd()}/{name}"
    input_data = json.load(in_file)
    input_data = input_data_validation(input_data)

    needs_create = not Path(service_path).exists()
    if needs_create:
        Path(service_path).mkdir(exist_ok=False)
    is_service_path_git_repo = (
        Path(service_path).joinpath(".git").exists()
        and Path(service_path).joinpath(".git").is_dir()
    )

    input_data[PLATFORM_SRC_DIR_PATH] = process_template(
        dest_base=Path(service_path),
        config={PLATFORM_SRC_DIR_PATH: input_data[PLATFORM_SRC_DIR_PATH]},
        skip_uuid=True,
        dry_run=dry_run,
    )[PLATFORM_SRC_DIR_PATH]

    write_text(
        data=input_data,
        path=Path(f"{service_path}/.launch_config"),
    )
    click.echo(f"Service configuration files have been written to {service_path}")

    if is_service_path_git_repo:
        click.echo(
            f"{service_path} appears to be a git repository! You will need to add, commit, and push these files manually."
        )
    else:
        if needs_create:
            click.echo(
                f"{service_path} was created, but has not yet been initialized as a git repository. You will need to initialize it."
            )
        else:
            click.echo(
                f"{service_path} already existed, but has not yet been initialized as a git repository. You will need to initialize it."
            )
