import logging

import click
from git.repo import Repo
from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository

logger = logging.getLogger(__name__)


def get_github_repos(
    g: Github, user: AuthenticatedUser | None = None
) -> list[Repository]:
    if user:
        return user.get_repos()
    repos = [repo for repo in g.get_user().get_repos()]
    logger.debug(f"Fetched {len(repos)}")
    return repos


def create_repository(
    g: Github,
    organization: str,
    name: str,
    description: str,
    public: bool,
    visibility: str,
    dry_run: True,
) -> Repo:
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have created a repo with the following, {name=} {description=} {public=} {visibility=} {organization=}",
                fg="yellow",
            )
            return

        return g.get_organization(organization).create_repo(
            name=name,
            description=description,
            private=not public,
            visibility=visibility,
            auto_init=True,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to create repository {name} in {organization}"
        ) from e


def repo_exist(name: str, g: Github) -> bool:
    try:
        g.get_repo(name)
        return True
    except Exception as e:
        logger.info(f"Repository {name} does not exist")
        return False
