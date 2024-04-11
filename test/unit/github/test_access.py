import logging
import re
from contextlib import ExitStack as does_not_raise

import pytest
import requests
import responses
from github.GithubException import UnknownObjectException

from launch.github import access


def test_access_grant_maintain(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_maintain(team, repo, dry_run=False)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_called_once()


def test_grant_maintain_dry_run(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_maintain(team, repo, dry_run=True)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_not_called()


def test_access_grant_admin(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_admin(team, repo, dry_run=False)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_called_once()


def test_grant_admin_dry_run(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_admin(team, repo, dry_run=True)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_not_called()


@pytest.mark.parametrize(
    "bad_status_codes", [400, 401, 402, 403, 404, 405, 500, 501, 502, 503, 504]
)
def test_set_require_approval_of_most_recent_reviewable_push_not_ok_raises(
    mocker, bad_status_codes
):
    organization = mocker.MagicMock()
    repository = mocker.MagicMock()
    branch = mocker.MagicMock()

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.PATCH,
            re.compile(".+"),
            body="",
            status=bad_status_codes,
            content_type="application/json",
        )
        with pytest.raises(RuntimeError):
            access.set_require_approval_of_most_recent_reviewable_push(
                organization=organization, repository=repository, branch=branch
            )


def test_set_require_approval_of_most_recent_reviewable_push_request_exception_raises(
    mocker,
):
    organization = mocker.MagicMock()
    repository = mocker.MagicMock()
    branch = mocker.MagicMock()

    mocker.patch.object(requests, "patch", side_effect=OSError)

    with pytest.raises(RuntimeError):
        access.set_require_approval_of_most_recent_reviewable_push(
            organization=organization, repository=repository, branch=branch
        )


@pytest.mark.parametrize(
    "repo_name, expected_slug, raises",
    [
        (
            "tf-cloud-wrapper_module-example",
            "terraform-administrators",
            does_not_raise(),
        ),
        (
            "depr-tf-aws-wrapper_module-lambda_function",
            "terraform-administrators",
            does_not_raise(),
        ),
        ("lcaf-component-platform", "lcaf-administrators", does_not_raise()),
        ("bad-prefix", None, pytest.raises(access.NoMatchingTeamException)),
    ],
)
def test_select_administrative_team(repo_name, expected_slug, raises, mocker):
    organization = mocker.MagicMock()
    repository = mocker.MagicMock()
    repository.name = repo_name

    with raises:
        result = access.select_administrative_team(
            repository=repository, organization=organization
        )
        organization.get_team_by_slug.assert_called_with(expected_slug)
        assert result is not None


class TestSelectPlatformTeam:
    def test_team_missing(self, mocker):
        organization = mocker.MagicMock()
        organization.get_team_by_slug.side_effect = UnknownObjectException
        with pytest.raises(access.NoMatchingTeamException) as exc_ctx:
            access.select_platform_team(organization=organization)
            assert str(access.DEFAULT_PLATFORM_TEAM_SLUGS) in exc_ctx
        assert organization.get_team_by_slug.call_count == 3

    def test_specified_platform_team_not_found(self, mocker):
        organization = mocker.MagicMock()
        organization.get_team_by_slug.side_effect = UnknownObjectException
        slug = "platform_slug"
        with pytest.raises(access.NoMatchingTeamException, match=slug):
            access.select_platform_team(organization=organization, team_name=slug)

    def test_happy_path(self, mocker):
        organization = mocker.MagicMock()
        result = access.select_platform_team(organization=organization)
        assert result is not None
        assert organization.get_team_by_slug.call_count == 1


class TestConfigureDefaultBranchProtection:
    def test_warns_on_default_branch_name(self, mocker, caplog):
        mocked_default_branch = mocker.MagicMock()
        mocked_default_branch.name = "not-main"

        repo = mocker.MagicMock()
        repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

        with caplog.at_level(logging.WARNING):
            access.configure_default_branch_protection(repository=repo, dry_run=True)
            assert len(caplog.records) > 0
            assert mocked_default_branch.name in caplog.text

    def test_happy_path(self, mocker):
        mocked_default_branch = mocker.MagicMock()
        mocked_default_branch.name = "main"

        repo = mocker.MagicMock()
        repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

        with mocker.patch.context_manager(
            access, "set_require_approval_of_most_recent_reviewable_push"
        ):
            access.configure_default_branch_protection(repository=repo, dry_run=False)
            access.set_require_approval_of_most_recent_reviewable_push.assert_called_once()

        mocked_default_branch.edit_protection.assert_called_once()
        mocked_default_branch.edit_required_pull_request_reviews.assert_called_once()
        mocked_default_branch.edit_protection.assert_called_once()

    def test_happy_path_dry_run(self, mocker):
        mocked_default_branch = mocker.MagicMock()
        mocked_default_branch.name = "main"

        repo = mocker.MagicMock()
        repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

        with mocker.patch.context_manager(
            access, "set_require_approval_of_most_recent_reviewable_push"
        ):
            access.configure_default_branch_protection(repository=repo, dry_run=True)
            access.set_require_approval_of_most_recent_reviewable_push.assert_not_called()

        mocked_default_branch.edit_protection.assert_not_called()
        mocked_default_branch.edit_required_pull_request_reviews.assert_not_called()
        mocked_default_branch.edit_protection.assert_not_called()

    @pytest.mark.parametrize("organization_login", access.LAUNCH_ORGS_USING_RULESETS)
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_does_not_apply_to_orgs_using_ruleset(
        self, organization_login, dry_run, mocker, caplog
    ):
        mocked_default_branch = mocker.MagicMock()
        mocked_default_branch.name = "main"

        repo = mocker.MagicMock()
        repo.organization.login = organization_login
        repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

        with caplog.at_level(level=logging.WARNING):
            access.configure_default_branch_protection(repository=repo, dry_run=dry_run)
        assert (
            "does not use branch protection rules. No action will be taken."
            in caplog.text
        )
