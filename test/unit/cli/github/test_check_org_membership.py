import pytest

from launch.cli.github.access import commands


@pytest.fixture
def mocked_github(mocker):
    mocked_gh = mocker.MagicMock()
    mocked_org = mocker.MagicMock()
    mocked_repo = mocker.MagicMock()
    mocked_pr = mocker.MagicMock()
    mocked_user = mocker.MagicMock()

    mocked_org.get_repo.return_value = mocked_repo
    mocked_repo.get_pull.return_value = mocked_pr
    mocked_pr.user = mocked_user
    mocked_gh.get_organization.return_value = mocked_org
    mocked_gh.get_user_by_id.return_value = mocked_user
    mocked_gh.get_user.return_value = mocked_user

    mocker.patch.object(commands, "get_github_instance", return_value=mocked_gh)

    yield mocked_gh, mocked_org, mocked_repo, mocked_pr, mocked_user


@pytest.fixture
def mocked_github_member(mocker, mocked_github):
    mocked_gh, mocked_org, mocked_repo, mocked_pr, mocked_user = mocked_github
    mocked_org.has_in_members = mocker.MagicMock(return_value=True)
    yield mocked_gh, mocked_org, mocked_repo, mocked_pr, mocked_user


@pytest.fixture
def mocked_github_nonmember(mocker, mocked_github):
    mocked_gh, mocked_org, mocked_repo, mocked_pr, mocked_user = mocked_github
    mocked_org.has_in_members = mocker.MagicMock(return_value=False)
    yield mocked_gh, mocked_org, mocked_repo, mocked_pr, mocked_user


class TestUserOrganization:
    def test_check_user_organization_fails_with_missing_params(self, cli_runner):
        result = cli_runner.invoke(
            commands.check_user_organization,
            [],
        )
        assert result.exception
        assert result.exit_code != 0
        assert "Either a --user-id or --user-name must be provided." in result.output

    def test_check_user_organization_by_id_ok(self, cli_runner, mocked_github_member):
        result = cli_runner.invoke(
            commands.check_user_organization,
            ["--organization", "phony_org", "--user-id", "12345"],
        )
        assert not result.exception
        assert result.exit_code == 0

    def test_check_user_organzation_by_name_ok(self, cli_runner, mocked_github_member):
        result = cli_runner.invoke(
            commands.check_user_organization,
            ["--organization", "phony_org", "--user-name", "phony_user"],
        )
        assert not result.exception
        assert result.exit_code == 0

    def test_check_user_organization_by_id_fails_nonzero(
        self, cli_runner, mocked_github_nonmember
    ):
        (
            mocked_gh,
            mocked_org,
            mocked_repo,
            mocked_pr,
            mocked_user,
        ) = mocked_github_nonmember

        result = cli_runner.invoke(
            commands.check_user_organization,
            ["--organization", "phony_org", "--user-id", "12345"],
        )
        mocked_org.has_in_members.assert_called_once_with(mocked_user)
        assert result.exception
        assert result.exit_code != 0

    def test_check_user_organization_by_name_fails_nonzero(
        self, cli_runner, mocked_github_nonmember
    ):
        (
            mocked_gh,
            mocked_org,
            mocked_repo,
            mocked_pr,
            mocked_user,
        ) = mocked_github_nonmember

        result = cli_runner.invoke(
            commands.check_user_organization,
            ["--organization", "phony_org", "--user-name", "phony_user"],
        )
        mocked_org.has_in_members.assert_called_once_with(mocked_user)
        assert result.exception
        assert result.exit_code != 0


class TestPullRequestOrganization:
    def test_check_pr_organization_fails_with_missing_repository_param(
        self, cli_runner
    ):
        result = cli_runner.invoke(
            commands.check_pr_organization,
            [],
        )
        assert result.exception
        assert result.exit_code != 0
        assert "Missing option '--repository'" in result.output

    def test_check_pr_organization_fails_with_missing_pr_number_param(self, cli_runner):
        result = cli_runner.invoke(
            commands.check_pr_organization,
            ["--repository", "phony_repo"],
        )
        assert result.exception
        assert result.exit_code != 0
        assert "Missing option '--pr-number'" in result.output

    def test_check_pr_organization_ok(self, cli_runner, mocked_github_member):
        result = cli_runner.invoke(
            commands.check_pr_organization,
            ["--repository", "phony_repo", "--pr-number", "12345"],
        )
        assert not result.exception
        assert result.exit_code == 0

    def test_check_pr_organization_fails_nonzero(
        self, cli_runner, mocked_github_nonmember
    ):
        (
            mocked_gh,
            mocked_org,
            mocked_repo,
            mocked_pr,
            mocked_user,
        ) = mocked_github_nonmember

        result = cli_runner.invoke(
            commands.check_pr_organization,
            ["--repository", "phony_repo", "--pr-number", "12345"],
        )
        mocked_org.has_in_members.assert_called_once_with(mocked_user)
        assert result.exception
        assert result.exit_code != 0
