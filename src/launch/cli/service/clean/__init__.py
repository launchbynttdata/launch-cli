import logging
import shutil

import click

from launch.config.common import BUILD_TEMP_DIR_PATH
from launch.constants.version import SEMANTIC_VERSION
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
    
    click.secho(f"VERSION = {SEMANTIC_VERSION}")

    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, nothing will be cleaned", fg="yellow"
        )

    delete_list = [
        BUILD_TEMP_DIR_PATH,
        ".repo",
        "components",
        ".pre-commit-config.yaml",
    ]
    for item in delete_list:
        try:
            if dry_run:
                click.secho(
                    f"[DRYRUN] Would have removed the following directory: {item=}",
                    fg="yellow",
                )
            else:
                shutil.rmtree(item)
                click.secho(
                    f"Deleted: {item=}",
                )
        except FileNotFoundError:
            click.secho(
                f"item not found. nothing to clean: {item=}",
                fg="red",
            )
