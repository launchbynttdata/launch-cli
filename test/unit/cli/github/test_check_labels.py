from launch.cli.github.repo.commands import check_labels


class TestCheckLabels:
    def test_check_labels_ok(self, cli_runner, mocker):
        _ = mocker.patch("launch.cli.github.repo.commands.get_github_instance")
        patched_labels = mocker.patch(
            "launch.cli.github.repo.commands.has_custom_labels"
        )
        patched_labels.return_value = True

        result = cli_runner.invoke(
            check_labels,
            ["--repository-name", "phony_name"],
        )
        assert not result.exception
        assert result.exit_code == 0

    def test_check_labels_not_ok(self, cli_runner, mocker):
        _ = mocker.patch("launch.cli.github.repo.commands.get_github_instance")
        patched_labels = mocker.patch(
            "launch.cli.github.repo.commands.has_custom_labels"
        )
        patched_labels.return_value = False

        result = cli_runner.invoke(
            check_labels,
            ["--repository-name", "phony_name"],
        )
        assert result.exception
        assert result.exit_code == 1
