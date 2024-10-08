from launch.cli.service.build import build


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
