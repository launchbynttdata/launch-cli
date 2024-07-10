import logging
import sys
import traceback
from pathlib import Path

import click

from launch.config.common import AWS_REGION
from launch.lib.j2props.j2props_utils import J2PropsTemplate

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--values",
    help="Path to the input yaml values file.  Ex: uat/application/input.yml",
)
@click.option(
    "--template",
    help="Absolute or relative path to the template file.  Ex: templates/application.properties",
)
@click.option(
    "--dry-run",
    help="(Optional) Perform a dry run that reports on what it would do.",
)
def render(
    values: str,
    template: str,
    dry_run: bool,
):
    """
    A Jinja2 template processor that adds a filter to replace keys in the input with values from AWS Secrets Manager

    Args:
        values: Path to the input yaml values file.  Ex: uat/application/input.yml
        template: Absolute or relative path to the template file.  Ex: templates/application.properties
        dry_run: (Optional) Perform a dry run that reports on what it would do.

    Returns:
        None
    """

    try:
        if not Path(template).exists():
            click.secho(
                f"[Error] Template file not found: : {template=}",
                fg="red",
            )
            return
        if not Path(values).exists():
            click.secho(
                f"[Error] Input yaml file not found: : {values=}",
                fg="red",
            )
            return
        J2PropsTemplate(AWS_REGION).generate_from_template(values, template)
    except Exception:
        traceback.print_exception(*sys.exc_info())
        sys.exit(1)
