import logging
import pathlib

import click
from git import GitCommandError, Repo

logger = logging.getLogger(__name__)


def acquire_repo(repo_path: pathlib.Path) -> Repo:
    try:
        return Repo(path=repo_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to get a Repo instance from path {repo_path}: {e}"
        ) from e


def checkout_branch(
    repository: Repo,
    target_branch: str,
    new_branch: bool = False,
    dry_run: bool = True,
) -> None:
    command_args = []
    if new_branch:
        command_args.append("-b")
    command_args.append(target_branch)

    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have checked out a branch: {repository=} {command_args=}",
                fg="yellow",
            )
            return

        repository.git.checkout(command_args)
        logger.info(f"Checked out branch {target_branch}")
    except GitCommandError as e:
        message = f"An error occurred while checking out {target_branch}"
        logger.exception(message)
        raise RuntimeError(message) from e


def clone_repository(
    repository_url: str,
    target: str,
    branch: str,
    dry_run: bool = True,
) -> Repo:
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have cloned repository: {repository_url=} {target=} {branch=}",
                fg="yellow",
            )
            return
        logger.info(
            f"Attempting to clone repository: {repository_url=} {target=} {branch=}"
        )
        repository = Repo.clone_from(url=repository_url, to_path=target, branch=branch)
    except GitCommandError as e:
        message = f"Error occurred while cloning the repository from {repository_url}"
        logger.exception(message)
        raise RuntimeError(message) from e
    return repository


def push_branch(
    repository: Repo, branch: str, commit_msg="Initial commit", dry_run: bool = True
) -> None:
    if dry_run:
        click.secho(
            f"[DRYRUN] Would have pushed a branch with the following, {repository=} {branch=} {commit_msg=}",
            fg="yellow",
        )
        return

    repository.git.add(["."])
    repository.git.commit(["-m", commit_msg])
    repository.git.push(["--set-upstream", "origin", branch])
    logger.info(f"Pushed the following branch: {repository=} {branch=} {commit_msg=}")
