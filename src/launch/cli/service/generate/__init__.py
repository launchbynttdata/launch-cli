import json
import logging
from pathlib import Path

import click

from launch.cli.service.clean import clean
from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME, LAUNCHCONFIG_PATH_LOCAL
from launch.lib.common.utilities import extract_repo_name_from_url
from launch.lib.local_repo.repo import clone_repository
from launch.lib.service.common import input_data_validation
from launch.lib.service.template.functions import (
    copy_and_render_templates,
    copy_template_files,
    list_jinja_templates,
    process_template,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--in-file",
    default=LAUNCHCONFIG_PATH_LOCAL,
    help=f"(Optional) The exact path to the {LAUNCHCONFIG_NAME} file. Defaults to {LAUNCHCONFIG_PATH_LOCAL}.",
)
@click.option(
    "--output-path",
    default=f"{Path().cwd()}/{BUILD_TEMP_DIR_PATH}",
    help=f"(Optional) The default output path for the build files. Defaults {BUILD_TEMP_DIR_PATH}",
)
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
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do.",
)
# TODO: Optimize this function and logic
# Ticket: 1633
@click.pass_context
def generate(
    context: click.Context,
    in_file: str,
    output_path: str,
    url: str,
    tag: str,
    dry_run: bool,
):
    """
    Dynamically generates terragrunt files based off a service.

    """
    context.invoke(
        clean,
        dry_run=dry_run,
    )

    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be created.", fg="yellow"
        )

    if not url and not Path(in_file).exists():
        click.secho(
            f"No .launch_config found. Please supply a path to the .launch_config file or a URL to repository with one.",
            fg="red",
        )
        return

    if url:
        service_dir = extract_repo_name_from_url(url)
    else:
        service_dir = Path.cwd().name
    build_path_service = f"{output_path}/{service_dir}"

    if url and Path(build_path_service).exists():
        click.secho(
            f"Service repo {build_path_service} exist locally but you have set the --url flag. Please remove the local build repo or remove the --url flag. Skipping cloning the respository.",
            fg="red",
        )
    elif url and not Path(build_path_service).exists():
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have cloned a repo with the following, {url=} {build_path_service=} {tag=}",
                fg="yellow",
            )
        else:
            clone_repository(
                repository_url=url,
                target=build_path_service,
                branch=tag,
            )

    if Path(LAUNCHCONFIG_PATH_LOCAL).exists():
        with open(LAUNCHCONFIG_PATH_LOCAL, "r") as f:
            click.secho(
                f"Reading config file found at local path: {LAUNCHCONFIG_PATH_LOCAL=}"
            )
            input_data = json.load(f)
            input_data = input_data_validation(input_data)
    elif Path(f"{build_path_service}/{LAUNCHCONFIG_NAME}").exists():
        with open(f"{build_path_service}/{LAUNCHCONFIG_NAME}", "r") as f:
            click.secho(
                f"Reading config file found at local path: {build_path_service}/{LAUNCHCONFIG_NAME}"
            )
            input_data = json.load(f)
            input_data = input_data_validation(input_data)
    else:
        click.secho(
            f"No {LAUNCHCONFIG_NAME} found. Exiting.",
            fg="red",
        )
        return

    skeleton_url = input_data["skeleton"]["url"]
    skeleton_tag = input_data["skeleton"]["tag"]
    build_skeleton_path = f"{output_path}/{extract_repo_name_from_url(skeleton_url)}"

    if dry_run:
        click.secho(
            f"[DRYRUN] Would have cloned a repo with the following, {skeleton_url=} {build_skeleton_path=} {skeleton_tag=}",
            fg="yellow",
        )
    else:
        clone_repository(
            repository_url=skeleton_url,
            target=build_skeleton_path,
            branch=skeleton_tag,
        )

    copy_template_files(
        src_dir=Path(build_skeleton_path),
        target_dir=Path(build_path_service),
        exclude_dir=PLATFORM_SRC_DIR_PATH,
        dry_run=dry_run,
    )

    input_data[PLATFORM_SRC_DIR_PATH] = process_template(
        src_base=Path(build_skeleton_path),
        dest_base=Path(build_path_service),
        config={PLATFORM_SRC_DIR_PATH: input_data[PLATFORM_SRC_DIR_PATH]},
        skip_uuid=True,
        dry_run=dry_run,
    )[PLATFORM_SRC_DIR_PATH]

    # Placing Jinja templates
    template_paths, jinja_paths = list_jinja_templates(
        Path(build_skeleton_path),
    )
    copy_and_render_templates(
        base_dir=Path(build_path_service),
        template_paths=template_paths,
        modified_paths=jinja_paths,
        context_data={"data": {"config": input_data}},
        dry_run=dry_run,
    )
