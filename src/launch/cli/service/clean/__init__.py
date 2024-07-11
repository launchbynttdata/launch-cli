import logging
import shutil

import click

from launch.config.common import BUILD_TEMP_DIR_PATH

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="(Optional) Perform a dry run that reports on what it would do.",
)
def clean(
    dry_run: bool,
):
    """
    Cleans up launch-cli build resources that are created from code generation. This command will delete all
    the files in the code build folder.

    Args:
        dry_run (bool): If set, it will not delete the resources, but will log what it would have
    """

    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be cleaned", fg="yellow"
        )

    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have removed the following directory: {BUILD_TEMP_DIR_PATH=}",
                fg="yellow",
            )
        else:
            shutil.rmtree(BUILD_TEMP_DIR_PATH)
            click.secho(
                f"Deleted directory: {BUILD_TEMP_DIR_PATH=}",
            )
    except FileNotFoundError:
        click.secho(
            f"Directory not found. nothing to clean: {BUILD_TEMP_DIR_PATH=}",
            fg="red",
        )
