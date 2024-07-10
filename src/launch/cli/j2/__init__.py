import click

from .render import render


@click.group(name="j2")
def j2_group():
    """Command family for j2-related tasks."""


j2_group.add_command(render)
