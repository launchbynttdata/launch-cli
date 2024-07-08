import logging
import pathlib

import click

from launch.lib.automation.helm.functions import (
    resolve_dependencies as resolve_helm_dependencies,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--path",
    default=pathlib.Path.cwd(),
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="Path to a folder containing your Chart.yaml. Defaults to the current working directory.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Simulate the execution of the command without making any changes.",
)
def resolve_dependencies(path: pathlib.Path, dry_run: bool):
    """Resolves nested dependencies for a Helm chart."""
    try:
        click.secho(f"Resolving Helm dependencies in {path}.", fg="green")
        resolve_helm_dependencies(
            helm_directory=path, global_dependencies={}, dry_run=dry_run
        )
    except Exception as e:
        click.secho(f"An error occurred while resolving Helm dependencies.", fg="red")
        logger.exception(e)
