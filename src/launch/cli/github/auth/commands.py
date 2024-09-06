import click

from launch.config.github import (
    GITHUB_APPLICATION_ID,
    GITHUB_INSTALLATION_ID,
    GITHUB_SIGNING_CERT_FILE,
    GITHUB_SIGNING_CERT_SECRET_NAME,
)
from launch.lib.github.generate_github_token import get_token_with_file, get_token_with_secret_name
from launch.lib.automation.common.functions import single_true


def validate_max_seconds(ctx, param, value):
    if value > 600:
        raise click.BadParameter("The maximum allowed value is 600.")
    return value


@click.command()
# BUG: this does not actually pull from AWS System Manager
@click.option(
    "--application-id-parameter-name",
    required=True,
    default=GITHUB_APPLICATION_ID,
    type=str,
    help=f"Name of the parameter from AWS System Manager parameter store that contains the application id of the GitHub App.",
)
# BUG: this does not actually pull from AWS System Manager
@click.option(
    "--installation-id-parameter-name",
    required=True,
    default=GITHUB_INSTALLATION_ID,
    type=str,
    help="Name of the parameter from AWS System Manager parameter store that contains the installation id of the GitHub App.",
)
@click.option(
    "--signing-cert-file",
    required=False,
    default=GITHUB_SIGNING_CERT_FILE,
    type=str,
    help="File containing the signing certificate of the GitHub App.",
)
@click.option(
    "--signing-cert-secret-name",
    required=False,
    default=GITHUB_SIGNING_CERT_SECRET_NAME,
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
    signing_cert_file: str | None,
    signing_cert_secret_name: str | None,
    token_expiration_seconds: int,
):
    if not single_true(
        [
            signing_cert_file,
            signing_cert_secret_name,
        ]
    ):
        message = (
            "You must specify a value with one of the following flags: --signing-cert-file, --signing-cert-secret-name"
        )
        click.secho(message, fg="red")
        raise RuntimeError(message)

    if signing_cert_file:
        token = get_token_with_file(
            application_id=application_id_parameter_name,
            installation_id=installation_id_parameter_name,
            signing_cert_file=signing_cert_file,
            token_expiration_seconds=token_expiration_seconds,
        )
    else:
        token = get_token_with_secret_name(
            application_id=application_id_parameter_name,
            installation_id=installation_id_parameter_name,
            signing_cert_secret_name=signing_cert_secret_name,
            token_expiration_seconds=token_expiration_seconds,
        )

    print(token)
    return token
