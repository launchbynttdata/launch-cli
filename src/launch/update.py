import logging

from semver import Version

from launch.config.github import GITHUB_ORG_NAME, GITHUB_REPO_NAME
from launch.constants.version import SEMANTIC_VERSION
from launch.lib.github.auth import get_anonymous_github_instance
from launch.lib.github.tags import get_repo_semantic_versions

logger = logging.getLogger(__name__)


def latest_version(
    versions: list[Version], include_prerelease: bool = False
) -> Version | None:
    """Narrow a list of versions down to a version that is newer than our current version, if possible. If the current version
    is supplied in the versions list, it will be treated as if it's an older version (not returned), so that we don't prompt a
    user to update to the version they're currently running. Prerelease versions are considered only if include_prerelease is set.

    Args:
        versions (list[Version]): List of versions that are available.
        include_prerelease (bool, optional): Allow prerelease versions to be returned. Defaults to False.

    Returns:
        Version | None: The latest Version object, or None if no newer versions exist.
    """
    current_version = SEMANTIC_VERSION
    if not include_prerelease:
        versions = [v for v in versions if v.prerelease is None]
    greater_versions = [v for v in versions if v > current_version]
    if greater_versions:
        return max(greater_versions)


def check_for_updates(include_prerelease: bool = False) -> Version | None:
    """Checks the repository where this tool lives to see if any new versions are available.

    Args:
        include_prerelease (bool, optional): Include prerelease versions in the version search. Defaults to False.

    Returns:
        Version | None: If there's an update available, returns a Version, otherwise None.
    """
    try:
        # Very short timeout to limit the amount of time we spend on this if there's problems on the GitHub side.
        g = get_anonymous_github_instance(timeout=1)
        repo = g.get_repo(full_name_or_id=f"{GITHUB_ORG_NAME}/{GITHUB_REPO_NAME}")
        available_versions = get_repo_semantic_versions(repo=repo)
        return latest_version(
            versions=available_versions, include_prerelease=include_prerelease
        )
    except Exception as e:
        # If anything goes wrong, we'll just skip the update check and log to debug
        logger.debug(f"Failure during check_for_updates: {e}")
        pass
