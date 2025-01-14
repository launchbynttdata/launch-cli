import pytest
from git.repo import Repo

from launch.cli.github.version import commands


@pytest.fixture(scope="function")
def example_github_repo(tmp_path):
    temp_repo = Repo.init(path=tmp_path, initial_branch="main")
    tmp_path.joinpath("test.txt").write_text("Sample file")
    temp_repo.index.add("test.txt")
    temp_repo.index.commit("Added test.txt")
    temp_repo.create_tag("0.1.0")
    yield temp_repo


class TestVersionPredictionCLI:
    def test_predict_version_fails_with_missing_params(self, cli_runner):
        result = cli_runner.invoke(
            commands.predict,
            [],
        )
        assert result.exception
        assert result.exit_code != 0
        assert "Missing option '--source-branch'" in result.output

    @pytest.mark.parametrize(
        "branch_name, expected_version",
        [
            ("fix/foo", "0.1.1"),
            ("feature/bar", "0.2.0"),
            ("feature!/baz", "1.0.0"),
        ],
    )
    def test_predict_version_number(
        self, branch_name: str, expected_version: str, cli_runner, example_github_repo
    ):
        result = cli_runner.invoke(
            commands.predict,
            [
                "--source-branch",
                branch_name,
                "--repo-path",
                str(example_github_repo.working_dir),
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert result.output.strip() == expected_version

    @pytest.mark.parametrize(
        "branch_name, expected_type",
        [
            ("fix/foo", "patch"),
            ("feature/bar", "minor"),
            ("feature!/baz", "major"),
        ],
    )
    def test_predict_version_change_type(
        self, branch_name: str, expected_type: str, cli_runner, example_github_repo
    ):
        result = cli_runner.invoke(
            commands.predict,
            [
                "--source-branch",
                branch_name,
                "--repo-path",
                str(example_github_repo.working_dir),
                "--change-type",
            ],
        )
        assert not result.exception
        assert result.exit_code == 0
        assert result.output.strip() == expected_type
