import click

from launch.config.common import DEFAULT_CLOUD_PROVIDER

provider = click.option(
    "--provider",
    default=DEFAULT_CLOUD_PROVIDER,
    help=f"The cloud provider to use. Defaults to {DEFAULT_CLOUD_PROVIDER}.",
)
