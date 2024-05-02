import click

from .commands import branch_name


@click.group(name="validate")
def validate_group():
    """Command family for validation-related tasks."""


validate_group.add_command(branch_name)
