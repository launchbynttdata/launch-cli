import click
import logging
import os
from git import Repo
from pathlib import Path

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
from launch.lib.service.common import load_launchconfig
from launch.lib.service.build.functions import execute_build
from launch.lib.service.template.launchconfig import LaunchConfigTemplate

logger = logging.getLogger(__name__)


@click.command()
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
    "--registry-type",
    default="docker",
    help="Based off of the registry-type value, the sequence of make commands used before build is decided. For example, if the registry-type is npm, the sequence of make commands will be make install, make build, and make publish. If the registry-type is docker, the sequence of make commands will be make configure, make build, and make push. Defaults to 'docker'.",
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
    registry_type: str,
    url: str,
    tag: str,
    push: bool,
    skip_clone: bool,
    dry_run: bool,
):
    """
    Builds an application defined in a .launch_config file.

    Args:
        context: click.Context: The context of the click command.
        registry_type (str): The registry type to use. Examples include: "docker", "npm", "nuget".
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
            input_data=load_launchconfig()
            os.environ["CONTAINER_IMAGE_VERSION"] = Repo(Path().cwd()).head.object.hexsha
            url = input_data["sources"]["application"]["url"]
            tag = input_data["sources"]["application"]["tag"]
            service_dir = service_dir.joinpath(extract_repo_name_from_url(url))

    provider = LaunchConfigTemplate(dry_run).get_provider("service", input_data)

    if Path(DOCKER_FILE_NAME).exists():
        execute_build(
            service_dir=Path.cwd(),
            registry_type=registry_type,
            push=push,
            provider=provider,
            dry_run=dry_run,
        )
        quit()

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
        registry_type=registry_type,
        push=push,
        provider=provider,
        dry_run=dry_run,
    )
