import logging
import pathlib

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
    repository: Repo, target_branch: str, new_branch: bool = False
) -> None:
    command_args = []
    if new_branch:
        command_args.append("-b")
    command_args.append(target_branch)

    try:
        logger.debug(f"{repository}: git checkout {' '.join(command_args)}")
        repository.git.checkout(command_args)
        logger.info(f"Checked out branch {target_branch}")
    except GitCommandError as e:
        message = f"An error occurred while checking out {target_branch}"
        logger.exception(message)
        raise RuntimeError(message) from e


def clone_repository(repository_url: str, target: str, branch: str) -> Repo:
    try:
        logger.info(f"Attempting to clone repository: {repository_url} into {target}")
        repository = Repo.clone_from(repository_url, target, branch=branch)
        logger.info(f"Repository {repository_url} cloned successfully to {target}")
    except GitCommandError as e:
        message = f"Error occurred while cloning the repository from {repository_url}"
        logger.exception(message)
        raise RuntimeError(message) from e
    return repository


def push_branch(repository: Repo, branch: str, commit_msg="Initial commit") -> None:
    logger.info(f"{repository=}, {branch=}, {commit_msg=}")
    repository.git.add(["."])
    repository.git.commit(["-m", commit_msg])
    repository.git.push(["--set-upstream", "origin", branch])
