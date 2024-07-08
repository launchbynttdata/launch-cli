import logging
import pathlib

from git.repo import Repo

logger = logging.getLogger(__name__)


def get_current_branch_name(repo_path: pathlib.Path) -> str:
    try:
        repo_instance = Repo(path=repo_path)
    except Exception as e:
        raise RuntimeError(f"{repo_path} is not a git repository!") from e
    return repo_instance.active_branch.name
