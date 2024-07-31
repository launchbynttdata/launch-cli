from pathlib import Path

import click

from launch.lib.github.generate_github_token import get_token


def validate_max_seconds(ctx, param, value):
    if value > 600:
        raise click.BadParameter("The maximum allowed value is 600.")
    return value


@click.command()
@click.option(
    "--application-id-parameter-name",
    required=True,
    type=str,
    help=f"Name of the parameter from AWS System Manager parameter store that contains the application id of the GitHub App.",
)
@click.option(
    "--installation-id-parameter-name",
    required=True,
    type=str,
    help="Name of the parameter from AWS System Manager parameter store that contains the installation id of the GitHub App.",
)
@click.option(
    "--signing-cert-secret-name",
    required=True,
    type=str,
    help="Name of the parameter from AWS System Manager parameter store that contains the name of the secret from AWS Secrets Manager that has the signing certificate of the GitHub App.",
)
@click.option(
    "--token-expiration-seconds",
    required=False,
    default=600,
    type=int,
    help="Number of seconds the token will be valid for. Default is 600 seconds.",
    callback=validate_max_seconds,
)
def application(
    application_id_parameter_name: str,
    installation_id_parameter_name: str,
    signing_cert_secret_name: str,
    token_expiration_seconds: int,
):
    token = get_token(
        application_id_parameter_name=application_id_parameter_name,
        installation_id_parameter_name=installation_id_parameter_name,
        signing_cert_secret_name=signing_cert_secret_name,
        token_expiration_seconds=token_expiration_seconds,
    )
    print(token)
    return token
