import click

from launch.config.aws import AWS_DEPLOYMENT_REGION, AWS_DEPLOYMENT_ROLE

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
