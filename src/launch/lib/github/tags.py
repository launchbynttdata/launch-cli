import itertools
import logging

from github.Repository import Repository
from github.Tag import Tag
from semver import Version

logger = logging.getLogger(__name__)


def get_repo_tags(repo: Repository) -> list[Tag]:
    tags = [tag for tag in repo.get_tags()]
    logger.debug(f"Fetched {len(tags)} tags from {repo.name}")
    return tags


def get_repo_semantic_versions(repo: Repository) -> list[Version]:
    def try_parse_version(tag_name: str) -> Version | None:
        try:
            return Version.parse(version=tag_name)
        except Exception as e:
            logger.debug(f"Failed to parse version from tag {tag_name}: {e}")

    tags = get_repo_tags(repo=repo)
    versions = list(
        itertools.filterfalse(
            lambda x: x is None, [try_parse_version(t.name) for t in tags]
        )
    )
    logger.debug(f"Successfully parsed {len(versions)} from tags on {repo.name}")
    return versions
