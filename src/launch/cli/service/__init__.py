import click

from .commands import cleanup, create, create_no_git, generate, update


@click.group(name="service")
def service_group():
    """Command family for service-related tasks."""


service_group.add_command(create)
service_group.add_command(generate)
service_group.add_command(cleanup)
service_group.add_command(update)
service_group.add_command(create_no_git)
