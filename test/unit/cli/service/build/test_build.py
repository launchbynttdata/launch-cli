from launch.cli.service.build import build

from unittest.mock import MagicMock


class TestBuild:
    def test_build_ok(self, cli_runner, mocker):
        result = cli_runner.invoke(
            build,
            ["--provider", "aws"],
        )
        assert not result.exception
        assert result.exit_code == 0

    def test_build_dry_run(self, cli_runner, mocker):
        result = cli_runner.invoke(
            build,
            ["--provider", "aws", "--dry-run"],
        )

        assert not result.exception
        assert result.exit_code == 0

    def test_build_invalid_configuration(self, cli_runner, mocker):
        result = cli_runner.invoke(
            build,
            ["--provider", "aws", "--url", "invalid-url"],
        )

        assert result.exception
        assert result.exit_code == 1

    def test_build_with_mocked_launchconfig_name(self, cli_runner, mocker):
        mock_execute_build = mocker.patch("launch.lib.service.build.execute_build")
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_url = "https://github.com/fakerepo.git"
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        mock_execute_build.return_value = None

        result = cli_runner.invoke(
            build,
            ["--provider", "aws", "--url", mock_url],
        )

        assert not result.exception
        assert result.exit_code == 0
