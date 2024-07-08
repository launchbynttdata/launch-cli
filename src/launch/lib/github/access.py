import logging

import requests
from github.Branch import Branch
from github.Organization import Organization
from github.Permissions import Permissions
from github.Repository import Repository
from github.Team import Team

from .auth import github_headers

logging.getLogger("github.Requester").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class NoMatchingTeamException(Exception):
    pass


# Maps repo prefixes to the slug of the team responsible for administration
REPO_PREFIX_ADMIN_TEAM_SLUG: dict[str, str] = {
    "tf-": "terraform-administrators",
    "depr-tf-": "terraform-administrators",
    "caf-": "caf-administrators",
}


def grant_maintain(team: Team, repository: Repository, dry_run=True) -> None:
    expected_permissions = {
        "triage": True,
        "push": True,
        "pull": True,
        "maintain": True,
        "admin": False,
    }

    existing_permissions: Permissions = team.get_repo_permission(repo=repository)

    needs_update = False

    if existing_permissions is not None:
        for permission, value in expected_permissions.items():
            if not getattr(existing_permissions, permission) == value:
                needs_update = True
    else:
        needs_update = True

    if needs_update:
        if dry_run:
            logger.info(
                f"Would have granted maintain permissions to {team.slug} on {repository.url}"
            )
        else:
            logger.info(
                f"Granting maintain permissions to {team.slug} on {repository.url}"
            )
            team.set_repo_permission(repo=repository, permission="maintain")
    else:
        logger.warning(
            f"Permissions are already in place for {team.slug} on {repository.url}"
        )


def grant_admin(team: Team, repository: Repository, dry_run=True) -> None:
    expected_permissions = {
        "triage": True,
        "push": True,
        "pull": True,
        "maintain": True,
        "admin": True,
    }

    existing_permissions: Permissions = team.get_repo_permission(repo=repository)

    needs_update = False

    if existing_permissions is not None:
        for permission, value in expected_permissions.items():
            if not getattr(existing_permissions, permission) == value:
                needs_update = True
    else:
        needs_update = True

    if needs_update:
        if dry_run:
            logger.info(
                f"Would have granted admin permissions to {team.slug} on {repository.url}"
            )
        else:
            logger.info(
                f"Granting admin permissions to {team.slug} on {repository.url}"
            )
            team.set_repo_permission(repo=repository, permission="admin")
    else:
        logger.warning(
            f"Permissions are already in place for {team.slug} on {repository.url}"
        )


def configure_default_branch_protection(repository: Repository, dry_run=True) -> None:
    default_branch: Branch = repository.get_branch(repository.default_branch)
    if not default_branch.name == "main":
        logger.warning(
            f"Repository at {repository.url} uses default branch {default_branch.name}, should be main!"
        )

    default_protections = {
        "enforce_admins": False,
        "dismiss_stale_reviews": False,
        "require_code_owner_reviews": True,
        "required_approving_review_count": 2,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "block_creations": True,
        "required_conversation_resolution": False,
        "lock_branch": False,
        "allow_fork_syncing": True,
    }

    if dry_run:
        logger.info(
            f"Would have applied default branch protection to {default_branch.name} for repo {repository.url}"
        )
    else:
        logger.info(
            f"Applying default branch protection to {default_branch.name} for repo {repository.url}"
        )
        default_branch.edit_protection(**default_protections)
        default_branch.edit_required_pull_request_reviews(
            require_code_owner_reviews=True, required_approving_review_count=2
        )
        set_require_approval_of_most_recent_reviewable_push(
            organization=repository.organization,
            repository=repository,
            branch=default_branch,
        )


def set_require_approval_of_most_recent_reviewable_push(
    organization: Organization, repository: Repository, branch: Branch
) -> None:
    """Hack to work around the fact that PyGithub doesn't support setting this configuration natively.

    Args:
        organization (Organization): GitHub Organization
        repository (Repository): GitHub Repository
        branch (Branch): Repository Branch

    Raises:
        RuntimeError: Raised if there was an issue setting this configuration
    """
    url = f"https://api.github.com/repos/{organization.login}/{repository.name}/branches/{branch.name}/protection/required_pull_request_reviews"
    payload = {"require_last_push_approval": True}
    try:
        response = requests.patch(url=url, json=payload, headers=github_headers())
        if not response.ok:
            raise RuntimeError(
                f"Failed to set_require_approval_of_most_recent_reviewable_push to {url}: Status Code: {response.status_code} Body: {response.text}"
            )
    except RuntimeError as re:
        raise re
    except Exception as e:
        raise RuntimeError(
            f"Failed to set_require_approval_of_most_recent_reviewable_push to {url}"
        ) from e


def select_administrative_team(
    repository: Repository, organization: Organization
) -> Team:
    for name_prefix, team_slug in REPO_PREFIX_ADMIN_TEAM_SLUG.items():
        if repository.name.startswith(name_prefix):
            return organization.get_team_by_slug(team_slug)
    else:
        raise NoMatchingTeamException(
            f"Repository {repository.name} not matched for any known administrative team."
        )
