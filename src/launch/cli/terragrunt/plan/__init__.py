import logging
import os
from pathlib import Path

import click

from launch.cli.service.generate import generate
from launch.config.common import BUILD_TEMP_DIR_PATH
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.lib.automation.terragrunt.functions import (
    prepare_for_terragrunt,
    terragrunt_init,
    terragrunt_plan,
)
from launch.lib.common.utilities import extract_repo_name_from_url

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--url",
    help="(Optional) The URL of the repository to clone.",
)
@click.option(
    "--tag",
    default=SERVICE_MAIN_BRANCH,
    help=f"(Optional) The tag of the repository to clone. Defaults to {SERVICE_MAIN_BRANCH}",
)
@click.option(
    "--target-environment",
    default=os.environ.get("TARGETENV", "sandbox"),
    help="The target environment to run the terragrunt command against. Defaults to sandbox.",
)
@click.option(
    "--provider-config",
    default=None,
    help="Provider config as a string used for any specific config needed for certain providers. For example, AWS needs additional parameters to assume a deployment role. e.x {'provider':'aws','aws':{'role_to_assume':'arn:aws:iam::012345678912:role/myRole','region':'us-east-2'}}",
)
@click.option(
    "--generation",
    is_flag=True,
    default=False,
    help="If set, it will generate the terragrunt files.",
)
@click.option(
    "--skip-diff",
    is_flag=True,
    default=False,
    help="If set, it will ignore checking the diff between the pipeline and service changes.",
)
@click.option(
    "--platform-resource",
    default=None,
    help="If set, this will set the specified pipeline resource to run terragrunt against. Defaults to None. i.e. 'pipeline-provider'",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not perform any action.",
)
@click.pass_context
def plan(
    context: click.Context,
    url: str,
    tag: str,
    target_environment: str,
    provider_config: dict,
    generation: bool,
    skip_diff: bool,
    platform_resource: str,
    dry_run: bool,
) -> None:
    """
    Runs terragrunt plan against a git repository set up to be ran with launch-cli.

    Args:
        url (str): The URL of the repository to clone.
        tag (str): The tag of the repository to clone.
        target_environment (str): The target environment to run the terragrunt command against.
        provider_config (dict): Provider config as a string used for any specific config needed for certain providers.
        generation (bool): If set, it will generate the terragrunt files.
        skip_diff (bool): If set, it will ignore checking the diff between the pipeline and service changes.
        platform_resource (str): If set, this will set the specified pipeline resource to run terragrunt against.
        dry_run (bool): Perform a dry run that reports on what it would do, but does not perform any action.

    Returns:
        None
    """

    if dry_run:
        click.secho("Performing a dry run, nothing will be updated", fg="yellow")
        # TODO: add a dry run for terragrunt plan
        return

    if url or generation:
        build_path = (
            Path()
            .cwd()
            .joinpath(f"{BUILD_TEMP_DIR_PATH}/{extract_repo_name_from_url(url)}")
        )
    else:
        build_path = Path().cwd()

    if generation:
        context.invoke(
            generate,
            url=url,
            tag=tag,
            dry_run=dry_run,
        )

    run_dirs = prepare_for_terragrunt(
        target_environment=target_environment,
        provider_config=provider_config,
        platform_resource=platform_resource,
        skip_diff=skip_diff,
    )

    for run_dir in run_dirs:
        os.chdir(build_path.joinpath(run_dir))
        terragrunt_init(
            dry_run=dry_run,
        )
        terragrunt_plan(
            dry_run=dry_run,
        )
