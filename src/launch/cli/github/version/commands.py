import pathlib
import sys
from functools import wraps

import click

from launch.lib.local_repo.branch import get_current_branch_name
from launch.lib.local_repo.predict import predict_version
from launch.lib.local_repo.tags import (
    CommitNotTaggedException,
    CommitTagNotSemanticVersionException,
    create_version_tag,
    push_version_tag,
    read_semantic_tags,
    read_semantic_version_tag,
)


def version_required_options_wrapper(f):
    @wraps(f)
    @click.option(
        "--repo-path",
        type=click.Path(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            path_type=pathlib.Path,
        ),
        default=".",
        help="Work with the repository located at this path. Can be relative or absolute, defaults to the current directory.",
    )
    @click.option(
        "--source-branch",
        type=click.STRING,
        help="Name of the branch that should be used to predict the next semantic version.",
        required=True,
    )
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.command()
@version_required_options_wrapper
def predict(repo_path: pathlib.Path, source_branch: str):
    """Predicts the next semantic version for a repository."""

    try:
        predicted_version = predict_version(
            existing_tags=read_semantic_tags(repo_path=repo_path),
            branch_name=source_branch,
        )
        click.echo(predicted_version)
    except Exception as e:
        click.secho(
            f"Failed to predict next version for repository at {repo_path}: {e}",
            fg="red",
        )
        raise click.Abort()


@click.command()
@click.option(
    "--pipeline",
    type=click.BOOL,
    is_flag=True,
    help="Run this command in pipeline mode, which disables additional safety checks. End users should never need to specify this option, it should only be used in conjunction with pipelines that enforce a consistent repository state!",
)
@version_required_options_wrapper
def apply(repo_path: pathlib.Path, source_branch: str, pipeline: bool):
    """Predicts the next semantic version for a repository based on the provided source branch, then creates and pushes a tag.

    Run this command inside a repo that has had its branch merged to main in order to apply the next semantic version. When running this command locally, the repo *MUST* be on the `main` branch. For use with pipelines and detached HEADs, the --pipeline option may be supplied, which will skip the check to ensure that the branch is on main. Use of the --pipeline flag in non-pipeline scenarios is highly discouraged and may lead to improper tagging. User beware!
    """
    # Safeguard to ensure that we can't accidentally bump a version if the branch is being merged against anything but main.
    if not pipeline:
        active_branch = get_current_branch_name(repo_path=repo_path)
        if not active_branch == "main":
            click.secho(
                f"Failed to apply next version for repository at {repo_path}: repo is not on main branch!",
                fg="red",
            )
            raise click.Abort()

    try:
        predicted_version = predict_version(
            existing_tags=read_semantic_tags(repo_path=repo_path),
            branch_name=source_branch,
        )
    except Exception as e:
        click.secho(
            f"Failed to apply next version for repository at {repo_path} during prediction: {e}",
            fg="red",
        )
        raise click.Abort()

    try:
        existing_tag = read_semantic_version_tag(repo_path=repo_path)
        click.secho(
            f"Failed to apply next version for repository at {repo_path}: HEAD is already tagged {existing_tag}",
            fg="red",
        )
        sys.exit(2)
    except (CommitNotTaggedException, CommitTagNotSemanticVersionException):
        pass

    try:
        new_tag = create_version_tag(repo_path=repo_path, version=predicted_version)
        push_version_tag(repo_path=repo_path, tag=new_tag)
        click.echo(f"Version is now {predicted_version}")
    except Exception as e:
        click.secho(
            f"Failed to apply next version for repository at {repo_path} during tagging: {e}",
            fg="red",
        )
        raise click.Abort()
