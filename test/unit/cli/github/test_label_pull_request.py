import logging

import pytest
from github.GithubException import UnknownObjectException

from launch.cli.github.repo import commands


class TestLabelPullRequest:
    def test_github_retrieval_failure(self, cli_runner, mocker, caplog):
        mocked_github = mocker.patch(
            "launch.cli.github.repo.commands.get_github_instance"
        )
        mocked_github.side_effect = UnknownObjectException(
            status=404, data={"errors": [{"code": "not_found"}]}
        )

        with caplog.at_level(level=logging.DEBUG):
            result = cli_runner.invoke(
                commands.label_pull_request,
                ["--repository-name", "phony_name", "--pull-request-id", "1"],
            )
            assert result.exception
            assert result.exit_code != 0
            assert "Failed to retrieve repository" in caplog.text

    def test_pr_retrieval_failure(self, cli_runner, mocker, caplog):
        mocked_repo = mocker.MagicMock()
        mocked_repo.get_pull.side_effect = UnknownObjectException(
            status=404, data={"errors": [{"code": "not_found"}]}
        )
        mocked_github = mocker.MagicMock()
        mocked_github.get_repo.return_value = mocked_repo
        mocked_instance_getter = mocker.patch(
            "launch.cli.github.repo.commands.get_github_instance"
        )
        mocked_instance_getter.return_value = mocked_github

        with caplog.at_level(level=logging.DEBUG):
            result = cli_runner.invoke(
                commands.label_pull_request,
                ["--repository-name", "phony_name", "--pull-request-id", "1"],
            )
            assert result.exception
            assert result.exit_code != 0
            assert f"Failed to retrieve pull request #1" in caplog.text

    def test_pr_branch_name_invalid_failure(self, cli_runner, mocker, caplog):
        mocked_pr = mocker.MagicMock()
        mocked_pr.head.ref = "invalid_name"
        mocked_repo = mocker.MagicMock()
        mocked_repo.get_pull.return_value = mocked_pr
        mocked_github = mocker.MagicMock()
        mocked_github.get_repo.return_value = mocked_repo
        mocked_instance_getter = mocker.patch(
            "launch.cli.github.repo.commands.get_github_instance"
        )
        mocked_instance_getter.return_value = mocked_github

        with caplog.at_level(level=logging.DEBUG):
            result = cli_runner.invoke(
                commands.label_pull_request,
                ["--repository-name", "phony_name", "--pull-request-id", "1"],
            )
            assert result.exception
            assert result.exit_code != 0
            assert f"Failure when predicting change type" in caplog.text
            assert mocked_pr.head.ref in caplog.text

    @pytest.mark.parametrize(
        "branch_name, expected_change_type",
        [
            ("fix/should-patch", "patch"),
            ("patch/should-patch", "patch"),
            ("bug/should-patch", "patch"),
            ("dependabot/should-patch", "patch"),
            ("feature/should-minor", "minor"),
            ("bug!/should-major", "major"),
        ],
    )
    def test_happy_path(
        self, branch_name: str, expected_change_type: str, cli_runner, mocker
    ):
        mocked_pr = mocker.MagicMock()
        mocked_pr.head.ref = branch_name
        mocked_repo = mocker.MagicMock()
        mocked_repo.get_pull.return_value = mocked_pr
        mocked_github = mocker.MagicMock()
        mocked_github.get_repo.return_value = mocked_repo
        mocked_instance_getter = mocker.patch(
            "launch.cli.github.repo.commands.get_github_instance"
        )
        mocked_instance_getter.return_value = mocked_github
        get_label_spy = mocker.spy(commands, "get_label_for_change_type")

        result = cli_runner.invoke(
            commands.label_pull_request,
            ["--repository-name", "phony_name", "--pull-request-id", "1"],
        )
        assert not result.exception
        assert result.exit_code == 0
        get_label_spy.assert_called_with(
            repository=mocked_repo, change_type=expected_change_type
        )
        mocked_pr.add_to_labels.assert_called_with(mocked_repo.get_label())
