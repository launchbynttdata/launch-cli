import logging
import os
from functools import cache

from github import Auth, Consts, Github

logger = logging.getLogger(__name__)


@cache
def read_github_token() -> str:
    try:
        return os.environ["GITHUB_TOKEN"]
    except KeyError:
        raise RuntimeError(
            "ERROR: The GITHUB_TOKEN environment variable is not set. You must set this environment variable with the contents of your GitHub Personal Access Token (PAT) to use this script."
        )


@cache
def github_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {read_github_token()}"}


def get_github_instance(token: str | None = None, timeout: int | None = None) -> Github:
    if timeout is None:
        timeout = Consts.DEFAULT_TIMEOUT
    if not token:
        logger.debug("Token wasn't passed, reading from environment.")
        token = read_github_token()
    auth = Auth.Token(token)
    return Github(auth=auth, timeout=timeout)


def get_anonymous_github_instance(timeout: int | None = None) -> Github:
    if timeout is None:
        timeout = Consts.DEFAULT_TIMEOUT
    return Github(auth=None, timeout=timeout)
