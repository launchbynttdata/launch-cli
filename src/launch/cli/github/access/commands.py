import logging

import click

from launch.config.github import (
    GITHUB_ORG_NAME,
    GITHUB_ORG_PLATFORM_TEAM,
    GITHUB_ORG_PLATFORM_TEAM_ADMINISTRATORS,
)
from launch.lib.github.access import (
    NoMatchingTeamException,
    configure_default_branch_protection,
    grant_admin,
    grant_maintain,
    select_administrative_team,
)
from launch.lib.github.auth import get_github_instance

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
    if dry_run:
        click.secho(
            "[DRYRUN] Performing a dry run, would have made changes to GitHub.",
            fg="yellow",
        )
        return
    g = get_github_instance()

    organization = g.get_organization(login=organization)

    platform_team = organization.get_team_by_slug(GITHUB_ORG_PLATFORM_TEAM)
    platform_admin_team = organization.get_team_by_slug(
        GITHUB_ORG_PLATFORM_TEAM_ADMINISTRATORS
    )

    repository = organization.get_repo(name=repository_name)

    try:
        specific_admin_team = select_administrative_team(
            repository=repository, organization=organization
        )
    except NoMatchingTeamException:
        click.secho(
            "Couldn't match a domain-specific administrative team to your repository based on name. Only the Platform Admin team will be granted administrative access, you may need to manually update permissions on this repo!",
            fg="yellow",
        )
        specific_admin_team = None

    grant_maintain(team=platform_team, repository=repository, dry_run=dry_run)
    grant_admin(team=platform_admin_team, repository=repository, dry_run=dry_run)
    if specific_admin_team:
        grant_admin(team=specific_admin_team, repository=repository, dry_run=dry_run)
    configure_default_branch_protection(repository=repository, dry_run=dry_run)


@click.command("check-user")
@click.option(
    "--user-id",
    type=click.INT,
    help="The user ID of the user to check. Mutually exclusive with --user-name.",
)
@click.option(
    "--user-name",
    type=click.STRING,
    help="The user name of the user to check. Mutually exclusive with --user-id.",
)
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization to verify the user's membership. Defaults to the {GITHUB_ORG_NAME} organization.",
)
def check_user_organization(
    organization: str, user_id: int = None, user_name: str = None
):
    """Checks if a user is a member of an organization."""
    if user_id is None and user_name is None:
        click.secho("Either a --user-id or --user-name must be provided.")
        exit(-1)
    if not user_id is None and not user_name is None:
        click.secho("Only one of --user-id or --user-name can be provided.")
        exit(-2)

    g = get_github_instance()
    org = g.get_organization(login=organization)

    if user_id:
        user = g.get_user_by_id(user_id)
    else:
        user = g.get_user(login=user_name)

    if org.has_in_members(user):
        click.echo(f"{user.login} is a member of {org.login}")
    else:
        click.echo(f"{user.login} is not a member of {org.login}")
        exit(1)


@click.command("check-pr")
@click.option(
    "--repository",
    envvar="GIT_REPO",
    type=click.STRING,
    required=True,
    help="The Repository where the pull request was opened.",
)
@click.option(
    "--pr-number",
    type=click.INT,
    required=True,
    help="The ID of the pull request to check.",
)
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization to verify the user's membership. Defaults to the {GITHUB_ORG_NAME} organization.",
)
def check_pr_organization(repository: str, pr_number: int, organization: str):
    """Checks if a pull request originated from inside the organization or from outside."""
    g = get_github_instance()
    org = g.get_organization(login=organization)
    pr = org.get_repo(repository).get_pull(pr_number)
    user = pr.user

    if org.has_in_members(user):
        click.echo(f"{user.login} is a member of {org.login}")
    else:
        click.echo(f"{user.login} is not a member of {org.login}")
        exit(1)
