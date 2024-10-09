from unittest.mock import MagicMock
from pathlib import Path

from launch.cli.service.build import build


class TestBuild:
    def test_build_default(self, cli_runner, mocker):
        fake_dir = Path("/fake/dir")
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

        # Mock the file system path to avoid FileNotFoundError
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs", return_value=True)
        mocker.patch("builtins.open", mocker.mock_open())

        # Call the build function
        result = cli_runner.invoke(
            build, ["--registry-type", registry_type, "--url", mock_url, "--tag", tag]
        )

        # Debugging outputs
        print(f"Output: {result.output}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Exception: {result.exception}")

        # Assertions
        assert not result.exception
        assert result.exit_code == 0

        mock_execute_build.assert_called_once_with(
            service_dir=fake_dir, registry_type=registry_type, push=False, dry_run=False
        )
