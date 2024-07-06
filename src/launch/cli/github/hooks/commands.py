import json

import click

from launch.config.github import GITHUB_ORG_NAME
from launch.lib.github.auth import get_github_instance
from launch.lib.github.hooks import create_hook


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization containing your repository. Defaults to the {GITHUB_ORG_NAME} organization.",
)
@click.option(
    "--repository-name", required=True, help="Name of the repository to be updated."
)
@click.option(
    "--name",
    default="web",
    help="Use web to create a webhook. Default: web. This parameter only accepts the value web.",
)
@click.option(
    "--url", required=True, help="The URL to which the payloads will be delivered."
)
@click.option(
    "--content-type",
    default="json",
    help="The media type used to serialize the payloads. Supported values include json and form. The default for the launch-cli is json.",
)
@click.option(
    "--secret",
    help="If provided, the secret will be used as the key to generate the HMAC hex digest value for delivery signature headers.",
)
@click.option(
    "--insecure-ssl",
    default=0,
    help="Determines whether the SSL certificate of the host for url will be verified when delivering payloads. Supported values include 0 (verification is performed) and 1 (verification is not performed). The default is 0. We strongly recommend not setting this to 1 as you are subject to man-in-the-middle and other attacks.",
)
@click.option(
    "--events",
    default='["push"]',
    help="Determines what events the hook is triggered for. Default: '[\"push\"]'",
)
@click.option(
    "--active",
    default=True,
    help="Determines if notifications are sent when the webhook is triggered. Default is true.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def create(
    organization: str,
    repository_name: str,
    name: str,
    url: str,
    content_type: str,
    secret: str,
    insecure_ssl: int,
    events: str,
    active: bool,
    dry_run: bool,
):
    """Creates a webhook for a single repository."""
    g = get_github_instance()

    config = {
        "url": url,
        "content_type": content_type,
        "secret": secret,
        "insecure_ssl": insecure_ssl,
    }

    repository = g.get_organization(login=organization).get_repo(name=repository_name)
    if dry_run:
        click.secho(
            f"Performing a dry run, nothing will be updated in GitHub\n\
repository_name: ${repository_name}\n\
repository.name: ${repository.name}",
            fg="yellow",
        )
    create_hook(
        repo=repository,
        name=name,
        config=config,
        events=json.loads(events),
        active=active,
        dry_run=dry_run,
    )
