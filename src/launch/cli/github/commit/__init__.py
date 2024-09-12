import click

from .status import status_group


@click.group(name="commit")
def commit_group():
    """Command family for dealing with GitHub webhooks."""


commit_group.add_command(status_group)
