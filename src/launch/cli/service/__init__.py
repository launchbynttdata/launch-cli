import click

from .commands import clean, create, generate, update


@click.group(name="service")
def service_group():
    """Command family for service-related tasks."""


service_group.add_command(create)
service_group.add_command(generate)
service_group.add_command(clean)
service_group.add_command(update)
