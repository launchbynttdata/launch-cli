import logging
import pathlib

import click

from launch.lib.automation.helm.functions import (
    resolve_dependencies as resolve_helm_dependencies,
)
from launch.lib.automation.helm.functions import run_deployment as run_helm_deployment
from launch.lib.automation.helm.functions import template_chart as run_helm_template

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
    "--release-name",
    required=True,
    help="Name of the Helm release.",
)
@click.option(
    "--namespace",
    required=True,
    help="Kubernetes namespace to deploy the chart into.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Simulate the execution of the command without making any changes.",
)
def run_deployment(
    path: pathlib.Path, release_name: str, namespace: str, dry_run: bool
):
    """Execute the Helm deployment."""
    try:
        click.secho(f"Running Helm deployment in {path}.", fg="green")
        run_helm_deployment(
            helm_directory=path,
            release_name=release_name,
            namespace=namespace,
            dry_run=dry_run,
        )
    except Exception as e:
        click.secho(f"An error occurred while running Helm deployment.", fg="red")
        logger.exception(e)


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
    "--release-name",
    required=True,
    help="Name of the Helm release.",
)
@click.option(
    "--namespace",
    required=True,
    help="Kubernetes namespace to deploy the chart into.",
)
def template_chart(path: pathlib.Path, release_name: str, namespace: str):
    """Execute the Helm template command."""
    try:
        click.secho(f"Running Helm template in {path}.", fg="green")
        output = run_helm_template(
            helm_directory=path,
            release_name=release_name,
            namespace=namespace,
        )
        click.echo(output)
    except Exception as e:
        click.secho(f"An error occurred while running Helm template.", fg="red")
        logger.exception(e)
