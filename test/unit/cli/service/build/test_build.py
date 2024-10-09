from unittest.mock import MagicMock

from launch.cli.service.build import build


class TestBuild:
    def test_build_ok(self, cli_runner, mocker):
        mock_execute_build = mocker.patch(
            "launch.lib.service.build.functions.execute_build"
        )
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_url = "https://github.com/fakerepo.git"
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        registry_type = "docker"
        tag = "latest"
        mock_execute_build.return_value = None

        mocker.patch("pathlib.Path.exists", return_value=True)
        mocker.patch("subprocess.run", return_value=MagicMock())

        result = cli_runner.invoke(
            build, ["--registry-type", registry_type, "--url", mock_url, "--tag", tag]
        )

        print(f"Output: {result.output}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Exception: {result.exception}")

        assert not result.exception
        assert result.exit_code == 0
