import itertools
import logging
import pathlib
import shutil

import click
from git import Repo
from ruamel.yaml import YAML

from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.constants.common import DISCOVERY_FORBIDDEN_DIRECTORIES

logger = logging.getLogger(__name__)


## Other Functions
def is_platform_git_changes(
    repository: Repo,
    commit_id: str,
    directory: str,
    main_branch: str = SERVICE_MAIN_BRANCH,
) -> bool:
    click.secho(
        f"Checking if git changes are exclusive to: {directory}",
    )
    origin = repository.remotes.origin
    origin.fetch()

    commit_main = repository.commit(f"origin/{main_branch}")

    # Check if the PR commit hash is the same as the commit sha of the main branch
    if commit_id == repository.rev_parse(f"origin/{main_branch}"):
        click.secho(
            f"Commit hash is the same as origin/{main_branch}",
        )
        commit_compare = repository.commit(f"origin/{main_branch}^")
    # PR commit sha is not the same as the commit sha of the main branch. Thus we want whats been changed since because
    # terragrunt will apply all changes.
    else:
        commit_compare = repository.commit(commit_id)

    # Get the diff between of the last commit only inside the platform/pipline directory
    exclusive_dir_diff = commit_compare.diff(
        commit_main, paths=directory, name_only=True
    )
    # Get the diff between of the last commit only outside the platform/pipline directory
    diff = commit_compare.diff(commit_main, name_only=True)
    excluding_dir_diff = [
        item.a_path for item in diff if not item.a_path.startswith(directory)
    ]

    # If there are no git changes, return false.
    if not exclusive_dir_diff:
        click.secho(
            f"No changes found in {directory}",
        )
        return False
    else:
        # If both are true, we want to throw to prevent simultaneous infrastructure and service changes.
        if excluding_dir_diff:
            message = f"Changes found in both inside and outside dir: {directory}"
            click.secho(
                message,
                fg="red",
            )
            raise RuntimeError(message)
        # If only the infrastructure directory has changes, return true.
        else:
            click.secho(
                f"Git changes only found in folder: {directory}",
            )
            return True


def discover_files(
    root_path: pathlib.Path,
    filename_partial: str = "",
    forbidden_directories: list[str] = None,
) -> list[pathlib.Path]:
    """Recursively discovers files underneath a top level root_path that match a partial name.

    Args:
        root_path (pathlib.Path): Top level directory to search
        filename_partial (str, optional): Case-insensitive part of the filename to search. Defaults to "", which will return all files. This partial search uses an 'in' expression, do not use a wildcard.
        forbidden_directories (list[str], optional): List of strings to match in directory names that will not be traversed. Defaults to None, which forbids traversal of some common directories (.git, .terraform, etc.). To search all directories, pass an empty list.

    Returns:
        list[pathlib.Path]: List of pathlib.Path objects for files matching filename_partial.
    """
    if forbidden_directories is None:
        forbidden_directories = DISCOVERY_FORBIDDEN_DIRECTORIES

    directories = [
        d
        for d in root_path.iterdir()
        if d.is_dir() and not d.name.lower() in forbidden_directories
    ]
    files = [
        f
        for f in root_path.iterdir()
        if not f.is_dir() and filename_partial in f.name.lower()
    ]
    files.extend(
        list(
            itertools.chain.from_iterable(
                [
                    discover_files(
                        root_path=d,
                        filename_partial=filename_partial,
                        forbidden_directories=forbidden_directories,
                    )
                    for d in directories
                ]
            )
        )
    )
    return files


def discover_directories(
    root_path: pathlib.Path,
    dirname_partial: str = "",
    forbidden_directories: list[str] = None,
) -> list[pathlib.Path]:
    """Recursively discovers subdirectories underneath a top level root_path that match a partial name. If a subdirectory doesn't match that partial name, none of its children will be searched.

    Args:
        root_path (pathlib.Path): Top level directory to search
        dirname_partial (str, optional): Case-insensitive part of the subdirectory name match. Defaults to "", which will return all subdirectories. This partial search uses an 'in' expression, do not use a wildcard.
        forbidden_directories (list[str], optional): List of strings to match in directory names that will not be traversed. Defaults to None, which forbids traversal of some common directories (.git, .terraform, etc.). To search all directories, pass an empty list.

    Returns:
        list[pathlib.Path]: List of pathlib.Path objects for files matching filename_partial.
    """

    if forbidden_directories is None:
        forbidden_directories = DISCOVERY_FORBIDDEN_DIRECTORIES

    directories = [
        d
        for d in root_path.iterdir()
        if d.is_dir()
        and dirname_partial in d.name
        and not d.name.lower() in forbidden_directories
    ]
    directories.extend(
        list(
            itertools.chain.from_iterable(
                [
                    discover_directories(
                        root_path=d,
                        dirname_partial=dirname_partial,
                        forbidden_directories=forbidden_directories,
                    )
                    for d in directories
                ]
            )
        )
    )
    return directories


def load_yaml(yaml_file: pathlib.Path) -> dict:
    """Instantiates a YAML parser and loads the content of a file containing YAML data.

    Args:
        yaml_file (pathlib.Path): Path to the YAML file

    Returns:
        dict: Dictionary containing the YAML structure
    """
    yaml_parser = YAML(typ="safe")
    yaml_contents: dict = yaml_parser.load(stream=yaml_file)
    return yaml_contents


def unpack_archive(
    archive_path: pathlib.Path,
    destination: pathlib.Path = pathlib.Path.cwd(),
    format_override: str = None,
) -> None:
    """Unpacks a single archive file to a desired destination directory. If the destination exists, it must be a directory. If it does not exist, it will be created.

    Args:
        archive_path (pathlib.Path): Path to a compressed archive
        destination (pathlib.Path, optional): Folder into which the archive will unpack, maintaining its internal packed structure. Defaults to pathlib.Path.cwd().
        format_override (str, optional): Override format detection with a particular format (one of "zip", "tar", "gztar", "bztar", or "xztar"). Defaults to None, which will detect format based on the filename.

    Raises:
        FileNotFoundError: Raised when the archive cannot be found
        FileExistsError: Raised when the destination exists but is not a directory.
    """
    if not archive_path.exists():
        raise FileNotFoundError(f"Supplied archive path {archive_path} does not exist!")

    if destination.exists() and not destination.is_dir():
        raise FileExistsError(
            f"Supplied destination {destination} exists but is not a directory!"
        )
    destination.mkdir(parents=True, exist_ok=True)

    if format_override is None:
        logger.debug(f"Unpacking archive {archive_path} to {destination}")
        shutil.unpack_archive(filename=archive_path, extract_dir=destination)
    else:
        logger.debug(
            f"Unpacking archive {archive_path} to {destination} with overridden format {format_override}"
        )
        shutil.unpack_archive(
            filename=archive_path, extract_dir=destination, format=format_override
        )


def single_true(list) -> bool:
    """
    Returns True if one and only one item in the list is True, otherwise returns False.

    Args:
        list (list): List of boolean values

    Returns:
        bool: True if one and only one item in the list is True, otherwise False.
    """
    i = iter(list)
    return any(i) and not any(i)
