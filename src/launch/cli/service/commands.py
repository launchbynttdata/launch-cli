import json
import logging
import shutil
from pathlib import Path
from typing import IO, Any

import click
from git import Repo

from launch.cli.github.access.commands import set_default
from launch.config.common import BUILD_DEPENDENCIES_DIR, CODE_GENERATION_DIR_SUFFIX
from launch.config.github import GITHUB_ORG_NAME
from launch.config.service import SERVICE_MAIN_BRANCH, SERVICE_REMOTE_BRANCH
from launch.lib.github.auth import get_github_instance
from launch.lib.github.repo import create_repository, repo_exist
from launch.lib.local_repo.repo import checkout_branch, clone_repository
from launch.lib.service.common import (
    copy_and_render_templates,
    determine_existing_uuid,
    input_data_validation,
    list_jinja_templates,
)
from launch.lib.service.functions import common_service_workflow, prepare_service

logger = logging.getLogger(__name__)


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--description",
    default="Service created with launch-cli.",
    help="A short description of the repository.",
)
@click.option(
    "--public",
    is_flag=True,
    default=False,
    help="The visibility of the repository.",
)
@click.option(
    "--visibility",
    default="private",
    help="The visibility of the repository. Can be one of: public, private.",
)
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--git-message",
    default="Initial commit",
    help="The git commit message to use when creating a commit. Defaults to 'Initial commit'.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will skip all actions with git. Overrides --skip-commit.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="If set, it will skip commiting the local changes.",
)
@click.option(
    "--skip-uuid",
    is_flag=True,
    default=False,
    help="If set, it will not generate a UUID to be used in skeleton files.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
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
    "--git-message",
    default="bot: launch service update commit",
    help="The git commit message to use when creating a commit. Defaults to 'bot: launch service update commit'.",
)
@click.option(
    "--uuid",
    is_flag=True,
    default=False,
    help="If set, it will generate a new UUID to be used in skeleton files.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="If set, it will skip commiting the local changes.",
)
@click.option(
    "--skip-sync",
    is_flag=True,
    default=False,
    help="If set, it will skip syncing the template files and only update the properties files and directories.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
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
    """Updates a service."""

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

    input_data["platform"] = determine_existing_uuid(
        input_data=input_data["platform"], path=service_path
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


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository and it's properties.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
# TODO: Optimize this function and logic
# Ticket: 1633
def generate(
    name: str,
    skip_git: bool,
    dry_run: bool,
):
    """Dynamically generates terragrunt files based off a service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")

    service_path = f"{Path.cwd()}/{name}"
    singlerun_path = f"{service_path}{CODE_GENERATION_DIR_SUFFIX}"

    if Path(singlerun_path).exists():
        click.secho(
            f"Generation repo {singlerun_path} already exist locally. Please remove this directory or run launch service cleanup.",
            fg="red",
        )
        return

    if not skip_git:
        g = get_github_instance()
        repo = g.get_repo(f"{GITHUB_ORG_NAME}/{name}")

        clone_repository(
            repository_url=repo.clone_url,
            target=name,
            branch=SERVICE_MAIN_BRANCH,
        )
    else:
        if not Path(service_path).exists():
            click.secho(
                f"Service repo {service_path} does not exist locally. Please remove the --skip-git flag to clone and continue generation.",
                fg="red",
            )
            return

    with open(f"{name}/.launch_config", "r") as f:
        input_data = json.load(f)
        input_data = input_data_validation(input_data)

    clone_repository(
        repository_url=input_data["skeleton"]["url"],
        target=singlerun_path,
        branch=input_data["skeleton"]["tag"],
    )

    shutil.copytree(
        f"{service_path}/{BUILD_DEPENDENCIES_DIR}",
        f"{singlerun_path}/{BUILD_DEPENDENCIES_DIR}",
        dirs_exist_ok=True,
    )
    shutil.copyfile(
        f"{service_path}/.launch_config", f"{singlerun_path}/.launch_config"
    )

    # Creating directories and copying properties files
    traverse_with_callback(
        dictionary=input_data["platform"],
        callback=callback_create_directories,
        base_path=singlerun_path,
    )
    traverse_with_callback(
        dictionary=input_data["platform"],
        callback=callback_copy_properties_files,
        base_path=singlerun_path,
    )

    # Placing Jinja templates
    template_paths, jinja_paths = list_jinja_templates(
        singlerun_path / Path(f"{BUILD_DEPENDENCIES_DIR}/jinja2")
    )
    copy_and_render_templates(
        base_dir=singlerun_path,
        template_paths=template_paths,
        modified_paths=jinja_paths,
        context_data={"data": {"config": input_data}},
    )

    # Remove the .launch directory
    shutil.rmtree(f"{singlerun_path}/.launch")


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def clean(
    name: str,
    dry_run: bool,
):
    """Cleans up launch-cli reources that are created from code generation."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be cleaned", fg="yellow")
        return

    code_generation_dir_name = f"{name}{CODE_GENERATION_DIR_SUFFIX}"
    code_generation_path = Path.cwd().joinpath(code_generation_dir_name)

    try:
        shutil.rmtree(code_generation_path)
        logger.info(f"Deleted the {code_generation_path} directory.")
    except FileNotFoundError:
        click.secho(
            f"Directory not found: {code_generation_path}",
            fg="red",
        )
