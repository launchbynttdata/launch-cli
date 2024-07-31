import click

from launch.config.aws import (
    AWS_DEPLOYMENT_REGION,
    AWS_DEPLOYMENT_ROLE,
    SM_AWS_PROFILE,
    SM_AWS_REGION,
)

aws_deployment_role = click.option(
    "--aws-deployment-role",
    default=AWS_DEPLOYMENT_ROLE,
    help="The AWS role to assume to deploy the resources into the AWS account.",
)

aws_deployment_region = click.option(
    "--aws-deployment-region",
    default=AWS_DEPLOYMENT_REGION,
    help="The AWS region to deploy the resources into.  Defaults to the AWS_REGION environment",
)

aws_secrets_region = click.option(
    "--aws-secrets-region",
    default=SM_AWS_REGION,
    help="Defines the AWS region to use for secrets retrieval. Default is AWS_REGION.",
)

aws_secrets_profile = click.option(
    "--aws-secrets-profile",
    default=SM_AWS_PROFILE,
    help="Defines the AWS profile to use for secrets retrieval. Secrets may not be in the same account as deploying to. Default is AWS_PROFILE.",
)
