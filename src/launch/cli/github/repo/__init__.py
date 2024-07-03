import click

from .commands import check_labels, create, create_labels, label_pull_request


@click.group(name="repo")
def repo_group():
    """Command family for dealing with GitHub repos."""


repo_group.add_command(create)
repo_group.add_command(check_labels)
repo_group.add_command(create_labels)
repo_group.add_command(label_pull_request)
