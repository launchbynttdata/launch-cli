import click
import os
import json
import logging
from pathlib import Path

from launch.cli.common.options import provider
from launch.cli.github.auth.commands import application
from launch.cli.service.clean import clean
from launch.config.aws import AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE
from launch.config.common import BUILD_TEMP_DIR_PATH, DOCKER_FILE_NAME
from launch.config.container import (
    CONTAINER_IMAGE_NAME,
    CONTAINER_IMAGE_VERSION,
    CONTAINER_REGISTRY,
)
from launch.config.github import (
    APPLICATION_ID_PARAMETER_NAME,
    DEFAULT_TOKEN_EXPIRATION_SECONDS,
    INSTALLATION_ID_PARAMETER_NAME,
    SIGNING_CERT_SECRET_NAME,
)
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.github.auth import read_github_token
from launch.lib.automation.environment.functions import (
    set_netrc,
    set_vars_from_bash_Var_file,
)
from launch.lib.common.utilities import extract_repo_name_from_url
from launch.lib.service.build import clone_if_no_dockerfile, execute_build

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
    "--container-registry",
    default=CONTAINER_REGISTRY,
    help=f"(Optional) The registry to push the built image to. Defaults to {CONTAINER_REGISTRY}",
)
@click.option(
    "--container-image-name",
    default=CONTAINER_IMAGE_NAME,
    help=f"(Optional) The name of the repository to clone. Defaults to {CONTAINER_IMAGE_NAME}",
)
@click.option(
    "--container-image-version",
    default=CONTAINER_IMAGE_VERSION,
    help=f"(Optional) The version of the repository to clone. Defaults to {CONTAINER_IMAGE_VERSION}",
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
    container_registry: str,
    container_image_name: str,
    container_image_version: str,
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
        container_registry: str: The registry to push the built image to.
        container_image_name: str: The name of the repository to clone.
        container_image_version: str: The version of the repository to clone.
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

    if container_image_name:
        os.environ["CONTAINER_IMAGE_NAME"] = container_image_name
    if container_image_version:
        os.environ["CONTAINER_IMAGE_VERSION"] = container_image_version
    if container_registry:
        os.environ["CONTAINER_REGISTRY"] = container_registry

    if Path(DOCKER_FILE_NAME).exists():
        execute_build(
            service_dir=Path.cwd(),
            provider=provider,
            push=push,
            dry_run=dry_run,
        )
        quit()

    if (
        APPLICATION_ID_PARAMETER_NAME
        and INSTALLATION_ID_PARAMETER_NAME
        and SIGNING_CERT_SECRET_NAME
    ):
        token = context.invoke(
            application,
            application_id_parameter_name=APPLICATION_ID_PARAMETER_NAME,
            installation_id_parameter_name=INSTALLATION_ID_PARAMETER_NAME,
            signing_cert_secret_name=SIGNING_CERT_SECRET_NAME,
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
                set_vars_from_bash_Var_file(AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE)
                temp_url = os.environ.get("GIT_SERVER_URL")
                temp_org = os.environ.get("GIT_ORG")
                temp_repo = os.environ.get("GIT_REPO")
                url = f"{temp_url}/{temp_org}/{temp_repo}.git"
                if not skip_clone:
                    clone_if_no_dockerfile(
                        url=url,
                        tag=os.environ.get("MERGE_COMMIT_ID"),
                        clone_dir=service_dir.joinpath(os.environ.get("GIT_REPO")),
                        service_dir=service_dir.joinpath(os.environ.get("GIT_REPO")),
                        dry_run=dry_run,
                    )
        else:
            with open(LAUNCHCONFIG_NAME, "r") as f:
                input_data = json.load(f)
                url = input_data["sources"]["application"]["url"]
                tag = input_data["sources"]["application"]["tag"]
                service_dir = service_dir.joinpath(extract_repo_name_from_url(url))
    else:
        if not skip_clone:
            clone_if_no_dockerfile(
                url=url,
                tag=tag,
                clone_dir=service_dir.joinpath(extract_repo_name_from_url(url)),
                service_dir=service_dir.joinpath(extract_repo_name_from_url(url)),
                dry_run=dry_run,
            )

    if service_dir.joinpath(
        f"{extract_repo_name_from_url(url)}/{LAUNCHCONFIG_NAME}"
    ).exists():
        with open(
            service_dir.joinpath(
                f"{extract_repo_name_from_url(url)}/{LAUNCHCONFIG_NAME}"
            ),
            "r",
        ) as f:
            input_data = json.load(f)
            url = input_data["sources"]["application"]["url"]
            tag = input_data["sources"]["application"]["tag"]
            service_dir = service_dir.joinpath(extract_repo_name_from_url(url))

    if not skip_clone:
        service_dir = clone_if_no_dockerfile(
            url=url,
            tag=tag,
            clone_dir=service_dir.joinpath(extract_repo_name_from_url(url)),
            service_dir=service_dir,
            dry_run=dry_run,
        )

    execute_build(
        service_dir=service_dir,
        provider=provider,
        push=push,
        dry_run=dry_run,
    )
