import logging
import sys
from pathlib import Path

import click

from launch.lib.local_repo.predict import validate_name
from launch.lib.local_repo.repo import acquire_repo


@click.command()
@click.option(
    "-b",
    "--branch-name",
    default="",
    help="Provide the exact name of a branch to be validated",
)
def branch_name(branch_name: str):
    """Validates that a branch name will be compatible with our semver handling. If this command is launched from within a Git repository, the current branch will be evaluated. This behavior can be overridden by the --branch-name flag."""

    cwd = Path.cwd()
    git_path = cwd.joinpath(".git")
    if git_path.exists() and git_path.is_dir():
        # We're in a Git repo
        if not branch_name:
            this_repo = acquire_repo(cwd)
            try:
                branch_name = this_repo.active_branch.name
            except TypeError as te:
                if "HEAD is a detached symbolic reference" in str(te):
                    click.secho(
                        "Current directory contains a git repo that has a detached HEAD. Check out a branch or supply the --branch-name parameter.",
                        fg="red",
                    )
                    sys.exit(-1)
                else:
                    raise
    if not branch_name:
        click.secho(
            "Current directory doesn't contain a git repo, you must provide a branch name with the --branch-name parameter."
        )
        sys.exit(-2)
    try:
        if not validate_name(branch_name=branch_name):
            raise Exception(f"Branch {branch_name} isn't valid!")
        click.secho(f"Branch {branch_name} is valid.", fg="green")
        sys.exit(0)
    except Exception as e:
        click.secho(e, fg="red")
        sys.exit(1)
