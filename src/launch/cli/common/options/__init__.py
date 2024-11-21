import click

from launch.config.aws import (
    AWS_DEPLOYMENT_REGION,
)
from launch.config.common import DEFAULT_CLOUD_PROVIDER

provider = click.option(
    "--provider",
    default=DEFAULT_CLOUD_PROVIDER,
    help=f"The cloud provider to use. Defaults to {DEFAULT_CLOUD_PROVIDER}.",
)

deployment_region = click.option(
    "--deployment-region",
    default=AWS_DEPLOYMENT_REGION,
    help="The AWS region to deploy the resources into.  Defaults to the AWS_REGION environment",
)