import click

from .commands import resolve_dependencies, run_deployment, template_chart


@click.group(name="helm")
def helm_group():
    """Command family for helm-related tasks."""


helm_group.add_command(resolve_dependencies)
helm_group.add_command(run_deployment)
helm_group.add_command(template_chart)
