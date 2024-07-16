import logging
import sys

import click

from launch.env import UPDATE_ALLOW_PRERELEASE, UPDATE_CHECK
from launch.update import check_for_updates


@click.command("version")
def get_version():
    """Prints the current version of the tool and immediately exits"""
    from launch.constants.version import SEMANTIC_VERSION

    logging.info(f"Launch CLI Version {SEMANTIC_VERSION}")
    sys.exit(0)


@click.group(name="cli", invoke_without_command=True)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    show_default=True,
    default=False,
    help="Increase verbosity of all subcommands",
)
@click.option(
    "--version",
    is_flag=True,
    show_default=True,
    default=False,
    help="Prints the current version of the tool and immediately exits.",
)
@click.pass_context
def cli(context: click.core.Context, verbose: bool, version: bool):
    """Launch CLI tooling to help automate common tasks performed by Launch engineers and their clients."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
        datefmt="%F %T %Z",
    )
    # breakpoint()
    if UPDATE_CHECK and not context.invoked_subcommand == "pipeline":
        new_version = check_for_updates(include_prerelease=UPDATE_ALLOW_PRERELEASE)
        if new_version:
            click.secho(
                f"Version {new_version} of Launch-CLI is now available!", fg="yellow"
            )
            click.secho(
                "To install the latest version, execute the following command: "
            )
            click.secho("    pip install --update launch-cli", fg="yellow")
    if context.invoked_subcommand is None and not version:
        click.echo(cli.get_help(context))
    if version:
        context.invoke(get_version)


from .github import github_group
from .helm import helm_group
from .j2 import j2_group
from .service import service_group
from .terragrunt import terragrunt
from .validate import validate_group

cli.add_command(get_version)
cli.add_command(github_group)
cli.add_command(service_group)
cli.add_command(helm_group)
cli.add_command(validate_group)
cli.add_command(j2_group)

cli.add_command(terragrunt)
