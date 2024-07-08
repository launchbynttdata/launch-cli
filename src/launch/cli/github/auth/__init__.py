import click

from .commands import application


@click.group(name="auth")
def auth_group():
    """Command family for dealing with generation of tokens using GitHub App."""


auth_group.add_command(application)
