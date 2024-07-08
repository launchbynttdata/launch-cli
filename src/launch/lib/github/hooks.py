import logging

from github.Repository import Repository

logger = logging.getLogger(__name__)


def create_hook(
    repo: Repository,
    name: str,
    config: dict[str, str],
    events: list[str],
    active: bool,
    dry_run: bool = True,
) -> None:
    if dry_run:
        logger.info(f"Would have created webhook on {repo.name} for repo {repo.url}")
    else:
        logger.info(f"Creating webhook on {repo.name} for repo {repo.url}")
        repo.create_hook(name=name, config=config, events=events, active=active)
