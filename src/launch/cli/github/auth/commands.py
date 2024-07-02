from pathlib import Path

import click

from launch.github.generate_github_token import get_token


@click.command()
@click.option(
    "--application_id_parameter_name",
    required=True,
    help=f"Name of the parameter from AWS System Manager parameter store that contains the application id of the GitHub App.",
)
@click.option(
    "--installation_id_parameter_name",
    required=True,
    help="Name of the parameter from AWS System Manager parameter store that contains the installation id of the GitHub App.",
)
@click.option(
    "--signing_cert_secret_name",
    required=True,
    help="Name of the parameter from AWS System Manager parameter store that contains the name of the secret from AWS Secrets Manager that has the signing certificate of the GitHub App.",
)
def application(
    application_id_parameter_name: str,
    installation_id_parameter_name: str,
    signing_cert_secret_name: str,
):
    token = get_token(
        application_id_parameter_name=application_id_parameter_name,
        installation_id_parameter_name=installation_id_parameter_name,
        signing_cert_secret_name=signing_cert_secret_name,
    )
    print(f"Generated GitHub Token: {token}")
