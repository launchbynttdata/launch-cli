import click

from launch.config.github import GITHUB_ORG_NAME
from launch.lib.github.auth import get_github_instance
from launch.lib.github.commit_status import (
    CommitStatusState,
    CommitStatusUpdatePayload,
    get_commit_status,
    set_commit_status,
)


@click.command("get")
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization containing your repository. Defaults to the {GITHUB_ORG_NAME} organization.",
)
@click.option(
    "--repository-name", required=True, help="Name of the repository to be updated."
)
@click.option("--commit-hash", required=True, help="Full SHA1 hash of a Git commit.")
@click.option(
    "--context",
    default="",
    help="A string label to differentiate this status from the status of other systems.",
)
def get(organization: str, repository_name: str, commit_hash: str, context: str):
    status = get_commit_status(
        get_github_instance(),
        repo_name=repository_name,
        repo_org=organization,
        commit_sha=commit_hash,
        context=context,
    )
    if not status:
        click.echo(
            f"No status found for {commit_hash} in {organization}/{repository_name}."
        )
        return
    click.echo(status.state)


@click.command("set")
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization containing your repository. Defaults to the {GITHUB_ORG_NAME} organization.",
)
@click.option(
    "--repository-name", required=True, help="Name of the repository to be updated."
)
@click.option("--commit-hash", required=True, help="Full SHA1 hash of a Git commit.")
@click.option(
    "--target-url",
    default="",
    help="The URL to link when setting a commit status message.",
)
@click.option(
    "--description",
    default="",
    help="A short message to associate with the commit status.",
)
@click.option(
    "--context",
    default="",
    help="A string label to differentiate this status from the status of other systems.",
)
@click.option(
    "--status",
    required=True,
    type=click.Choice(
        choices=[e.value for e in CommitStatusState], case_sensitive=False
    ),
    help="The status to set on the commit.",
)
def set(
    organization: str,
    repository_name: str,
    commit_hash: str,
    status: CommitStatusState,
    target_url: str,
    description: str,
    context: str,
):
    payload = CommitStatusUpdatePayload(
        state=CommitStatusState(status),
        target_url=target_url,
        description=description,
        context=context,
    )
    set_commit_status(
        git_connection=get_github_instance(),
        repo_name=repository_name,
        repo_org=organization,
        commit_sha=commit_hash,
        payload=payload,
    )


@click.group(name="status")
def status_group():
    """Command family for dealing with GitHub commit status."""


status_group.add_command(get)
status_group.add_command(set)
