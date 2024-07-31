import logging
import sys
import time
import traceback
from pathlib import Path

import click

from launch.cli.common.options.aws import aws_secrets_profile, aws_secrets_region
from launch.lib.j2props.j2props_utils import J2PropsTemplate

logger = logging.getLogger(__name__)


@click.command()
@aws_secrets_region
@aws_secrets_profile
@click.option(
    "--values",
    help="Path to the input yaml values file.  Ex: uat/application/input.yml",
)
@click.option(
    "--template",
    help="Absolute or relative path to the template file.  Ex: templates/application.properties",
)
@click.option(
    "--out-file",
    help="(Optional) Path to the output file.  Ex: output/application.properties (default: stdout)",
)
@click.option(
    "--type",
    default="non-secret",
    help="Type of template. Requires secret, non-secret. Default is non-secret.",
)
@click.option(
    "--dry-run",
    help="(Optional) Perform a dry run that reports on what it would do.",
)
def render(
    values: str,
    template: str,
    out_file: str,
    type: str,
    aws_secrets_profile: str,
    aws_secrets_region: str,
    dry_run: bool,
):
    """
    A Jinja2 template processor that adds a filter to replace keys in the input with values from AWS Secrets Manager

    Args:
        values: Path to the input yaml values file.  Ex: uat/application/input.yml
        template: Absolute or relative path to the template file.  Ex: templates/application.properties
        aws_secrets_profile: AWS profile to use for secrets lookup.
        aws_secrets_region: AWS region to use for secrets lookup.
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
        data = J2PropsTemplate(
            region=aws_secrets_region, profile=aws_secrets_profile
        ).generate_from_template(values, template)
        if out_file:
            with open(out_file, "w") as f:
                if dry_run:
                    click.secho(
                        f"[DRYRUN] Would have written to file: {out_file=}",
                        fg="yellow",
                    )
                else:
                    if type == "secret":
                        out_var = f"""
app_secrets = {{
{data}
}}
"""
                        f.write(out_var)
                    else:
                        out_var = f"""
app_environment = {{
timestamp={int(time.time())}
{data}
}}
"""
                        f.write(out_var)
        else:
            click.echo(data)
    except Exception:
        traceback.print_exception(*sys.exc_info())
        sys.exit(1)
