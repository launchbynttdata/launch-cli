import logging
import pathlib

from git import TagReference
from git.objects.commit import Commit
from semver import Version

from launch.lib.local_repo.repo import acquire_repo

logger = logging.getLogger(__name__)


class CommitNotTaggedException(Exception):
    pass


class CommitTagNotSemanticVersionException(Exception):
    pass


def read_tags(repo_path: pathlib.Path) -> list[str]:
    repo_instance = acquire_repo(repo_path=repo_path)
    all_tags = [tag.name for tag in repo_instance.tags]
    logger.debug(f"Discovered {len(all_tags)} tags")
    return all_tags


def read_semantic_tags(repo_path: pathlib.Path) -> list[Version]:
    all_tags = read_tags(repo_path=repo_path)
    semver_tags: list[Version] = []
    for tag in all_tags:
        try:
            parsed_tag = Version.parse(tag)
            semver_tags.append(parsed_tag)
        except ValueError:
            logger.debug(f"Dropping {tag=}, does not conform to semantic version")
    logger.debug(f"Narrowed to {len(semver_tags)} tags")
    return semver_tags


def read_version_tag(
    repo_path: pathlib.Path, commit: Commit | None = None
) -> TagReference:
    repo_instance = acquire_repo(repo_path=repo_path)
    if not commit:
        commit = repo_instance.head.object
    for discovered_tag in reversed(sorted(repo_instance.tags, key=lambda x: x.name)):
        if discovered_tag.commit == commit:
            return discovered_tag
    raise CommitNotTaggedException(f"{commit.hexsha if commit else 'HEAD'} is untagged")


def tag_is_semantic(tag: TagReference) -> bool:
    try:
        Version.parse(tag.name)
        return True
    except:
        return False


def read_semantic_version_tag(
    repo_path: pathlib.Path, commit: Commit | None = None
) -> Version:
    repo_instance = acquire_repo(repo_path=repo_path)
    if not commit:
        commit = repo_instance.head.object
    applicable_tags = list(filter(lambda x: x.commit == commit, repo_instance.tags))
    if not len(applicable_tags):
        raise CommitNotTaggedException()
    semantic_tags = list(filter(lambda x: tag_is_semantic(x), applicable_tags))
    if not len(semantic_tags):
        raise CommitTagNotSemanticVersionException()
    return Version.parse(sorted(semantic_tags, key=lambda x: x.name)[-1].name)


def create_version_tag(repo_path: pathlib.Path, version: Version) -> TagReference:
    repo_instance = acquire_repo(repo_path=repo_path)
    new_tag = repo_instance.create_tag(str(version))
    logger.info(f"Created {new_tag=}")
    return new_tag


def push_version_tag(
    repo_path: pathlib.Path, tag: TagReference, origin_name: str = "origin"
):
    repo_instance = acquire_repo(repo_path=repo_path)
    repo_instance.remote(origin_name).push(tag.name)
    logger.debug(f"Pushed {tag=} to {origin_name=}")
