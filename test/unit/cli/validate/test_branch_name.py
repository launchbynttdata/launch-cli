import pytest

from launch.cli.validate.commands import branch_name

ACCEPTABLE_BRANCH_NAMES = [
    "fix/ok",
    "fix!/ok",
    "patch/ok",
    "patch!/ok",
    "!patch/ok",
    "BUG/ok",
    "BUG!/ok",
    "!buG/ok",
    "feature/ok",
    "feature!/ok",
    "Feature/ok",
    "!Feature/ok",
    "feature/ok",
    "FEATURE/ok",
]

UNACCEPTABLE_BRANCH_NAMES = [
    "main",
    "foo/bar",
    "foo.bar",
    "aab20a1f33aa86ffae87b1786e6736f1c7e10d1d",  # pragma: allowlist secret
]


class TestBranchName:
    @pytest.mark.parametrize("create_branch_name", ACCEPTABLE_BRANCH_NAMES)
    def test_branch_name_valid_in_git_repo(
        self, create_branch_name, cli_runner, example_repo
    ):
        example_repo.git.checkout(["-b", create_branch_name])
        result = cli_runner.invoke(branch_name, [])
        assert not result.exception
        assert f"Branch {create_branch_name} is valid." in result.output

    @pytest.mark.parametrize("create_branch_name", UNACCEPTABLE_BRANCH_NAMES)
    def test_branch_name_valid_in_git_repo(
        self, create_branch_name, cli_runner, example_repo
    ):
        example_repo.git.checkout(["-b", create_branch_name])
        result = cli_runner.invoke(branch_name, [])
        assert result.exception
        assert f"Branch {create_branch_name} isn't valid!" in result.output

    def test_branch_name_invalid_outside_git_repo(self, cli_runner, working_dir):
        result = cli_runner.invoke(branch_name, [])
        assert result.exception
        assert "Current directory doesn't contain a git repo" in result.output

    @pytest.mark.parametrize("use_branch_name", ACCEPTABLE_BRANCH_NAMES)
    def test_branch_name_valid_outside_git_repo(
        self, use_branch_name, cli_runner, working_dir
    ):
        result = cli_runner.invoke(branch_name, ["--branch-name", use_branch_name])
        assert not result.exception
        assert f"Branch {use_branch_name} is valid." in result.output

    @pytest.mark.parametrize("use_branch_name", UNACCEPTABLE_BRANCH_NAMES)
    def test_branch_name_invalid_outside_git_repo(
        self, use_branch_name, cli_runner, working_dir
    ):
        result = cli_runner.invoke(branch_name, ["--branch-name", use_branch_name])
        assert result.exception
        assert f"Branch {use_branch_name} isn't valid!" in result.output
