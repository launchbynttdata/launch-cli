import logging

import pytest
from github.GithubException import GithubException

from launch.cli.github.repo.commands import create_labels


class TestCreateLabels:
    @pytest.mark.parametrize("labels_created", [0, 1, 1000])
    def test_create_labels_ok(self, labels_created: int, cli_runner, mocker, caplog):
        _ = mocker.patch("launch.cli.github.repo.commands.get_github_instance")
        patched_labels = mocker.patch(
            "launch.cli.github.repo.commands.create_custom_labels"
        )
        patched_labels.return_value = labels_created
        with caplog.at_level(level=logging.INFO):
            result = cli_runner.invoke(
                create_labels,
                ["--repository-name", "phony_name"],
            )
            assert not result.exception
            assert result.exit_code == 0
            assert str(labels_created) in caplog.text

    def test_create_labels_error(self, cli_runner, mocker, caplog):
        _ = mocker.patch("launch.cli.github.repo.commands.get_github_instance")
        patched_labels = mocker.patch(
            "launch.cli.github.repo.commands.create_custom_labels"
        )
        patched_labels.side_effect = GithubException(
            status=422, data={"errors": [{"code": "something_else"}]}
        )
        with caplog.at_level(level=logging.INFO):
            result = cli_runner.invoke(
                create_labels,
                ["--repository-name", "phony_name"],
            )
            assert result.exception
            assert result.exit_code != 0
