import click

from .commands import check_pr_organization, check_user_organization, set_default


@click.group(name="access")
def access_group():
    """Command family for dealing with GitHub access."""


access_group.add_command(set_default)
access_group.add_command(check_user_organization)
access_group.add_command(check_pr_organization)
