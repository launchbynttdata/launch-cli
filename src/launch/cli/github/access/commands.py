import logging
from contextlib import suppress

import click

from launch import GITHUB_ORG_NAME
from launch.github.access import (
    NoMatchingTeamException,
    configure_default_branch_protection,
    grant_admin,
    grant_maintain,
    select_administrative_team,
    select_platform_team,
)
from launch.github.auth import get_github_instance

logger = logging.getLogger(__name__)


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
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not update access.",
)
def set_default(organization: str, repository_name: str, dry_run: bool):
    """Sets the default access and branch protections for a single repository."""
    display_manual_update_message = False
    g = get_github_instance()

    organization = g.get_organization(login=organization)
    repository = organization.get_repo(name=repository_name)

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated in GitHub", fg="yellow"
        )

    try:
        platform_team = select_platform_team(organization=organization)
        grant_maintain(team=platform_team, repository=repository, dry_run=dry_run)
    except Exception as e:
        click.secho(f"Failed to set permissions for the platform team: {e}", fg="red")
        display_manual_update_message = True

    try:
        platform_admin_team = organization.get_team_by_slug("platform-administrators")
        grant_admin(team=platform_admin_team, repository=repository, dry_run=dry_run)
    except Exception as e:
        click.secho(
            f"Failed to set permissions for the platform adminstrators team: {e}",
            fg="red",
        )
        display_manual_update_message = True

    try:
        specific_admin_team = select_administrative_team(
            repository=repository, organization=organization
        )
        grant_admin(team=specific_admin_team, repository=repository, dry_run=dry_run)
    except NoMatchingTeamException:
        click.secho(
            "Couldn't match a domain-specific administrative team to your repository based on name.",
            fg="yellow",
        )
        display_manual_update_message = True

    configure_default_branch_protection(repository=repository, dry_run=dry_run)
    if display_manual_update_message:
        click.secho(
            "One or more failures occurred during permission assignment. You may need to manually update permissions on this repo!",
            fg="yellow",
        )
