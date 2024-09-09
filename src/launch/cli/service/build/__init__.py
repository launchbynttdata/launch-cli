import click
import json
import logging
import os
from pathlib import Path

from launch.cli.common.options import provider
from launch.cli.github.auth.commands import application
from launch.cli.service.clean import clean
from launch.config.aws import AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE
from launch.config.common import BUILD_TEMP_DIR_PATH, DOCKER_FILE_NAME
from launch.config.github import (
    GITHUB_APPLICATION_ID,
    DEFAULT_TOKEN_EXPIRATION_SECONDS,
    GITHUB_INSTALLATION_ID,
    GITHUB_SIGNING_CERT_SECRET_NAME,
)
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.github.auth import read_github_token
from launch.lib.automation.environment.functions import (
    readFile,
    set_netrc,
)
from launch.lib.common.utilities import extract_repo_name_from_url
from launch.lib.local_repo.repo import clone_repository, checkout_branch
from launch.lib.service.build import execute_build

logger = logging.getLogger(__name__)


@click.command()
@provider
@click.option(
    "--url",
    default=None,
    help="(Optional) The URL of the repository to clone.",
)
@click.option(
    "--tag",
    default=SERVICE_MAIN_BRANCH,
    help=f"(Optional) The tag of the repository to clone. Defaults to None",
)
@click.option(
    "--push",
    is_flag=True,
    default=False,
    help="(Optional) Will push the built image to the repository.",
)
@click.option(
    "--skip-clone",
    is_flag=True,
    default=False,
    help="(Optional) Skip cloning the application files. Will assume you're in a directory with the application files.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do.",
)
@click.pass_context
def build(
    context: click.Context,
    provider: str,
    url: str,
    tag: str,
    push: bool,
    skip_clone: bool,
    dry_run: bool,
):
    """
    Builds an application defined in a .launch_config file.

    Ars:
        context: click.Context: The context of the click command.
        provider (str): The cloud provider to use.
        url: str: The URL of the repository to clone.
        tag: str: The tag of the repository to clone.
        push: bool: Will push the built image to the repository.
        skip_clone: bool: Skip cloning the application files.
        dry_run: bool: Perform a dry run that reports on what it would do.

    Returns:
        None
    """
    context.invoke(
        clean,
        dry_run=dry_run,
    )

    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be built.", fg="yellow"
        )

    if Path(DOCKER_FILE_NAME).exists():
        execute_build(
            service_dir=Path.cwd(),
            provider=provider,
            push=push,
            dry_run=dry_run,
        )
        quit()

    if (
        GITHUB_APPLICATION_ID
        and GITHUB_INSTALLATION_ID
        and GITHUB_SIGNING_CERT_SECRET_NAME
    ):
        token = context.invoke(
            application,
            application_id_parameter_name=GITHUB_APPLICATION_ID,
            installation_id_parameter_name=GITHUB_INSTALLATION_ID,
            signing_cert_secret_name=GITHUB_SIGNING_CERT_SECRET_NAME,
            token_expiration_seconds=DEFAULT_TOKEN_EXPIRATION_SECONDS,
        )
    else:
        token = read_github_token()

    set_netrc(
        password=token,
        dry_run=dry_run,
    )

    input_data = None
    service_dir = Path.cwd().joinpath(BUILD_TEMP_DIR_PATH)

    if not url:
        if not Path(LAUNCHCONFIG_NAME).exists():
            if not Path(AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE).exists():
                click.secho(
                    f"No {LAUNCHCONFIG_NAME} found or a {AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}. Please rerun command with appropriate {LAUNCHCONFIG_NAME},{AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE}, --in-file, or --url",
                    fg="red",
                )
                quit()
            else:
                temp_server_url = readFile("GIT_SERVER_URL")
                temp_org = readFile("GIT_ORG")
                temp_repo = readFile("GIT_REPO")
                url = f"{temp_server_url}/{temp_org}/{temp_repo}"
                tag = readFile("MERGE_COMMIT_ID")
                os.environ["CONTAINER_IMAGE_VERSION"] = readFile(
                    "CONTAINER_IMAGE_VERSION"
                )
                service_dir = service_dir.joinpath(extract_repo_name_from_url(url))
        else:
            with open(LAUNCHCONFIG_NAME, "r") as f:
                input_data = json.load(f)
                url = input_data["sources"]["application"]["url"]
                tag = input_data["sources"]["application"]["tag"]
                service_dir = service_dir.joinpath(extract_repo_name_from_url(url))

    if not skip_clone:
        repository = clone_repository(
            repository_url=url,
            target=service_dir,
            branch=SERVICE_MAIN_BRANCH,
            dry_run=dry_run,
        )
        checkout_branch(
            repository=repository,
            target_branch=tag,
            dry_run=dry_run,
        )

    execute_build(
        service_dir=service_dir,
        provider=provider,
        push=push,
        dry_run=dry_run,
    )
