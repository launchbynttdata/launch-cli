from pathlib import Path

from launch.cli.service.commands import create_no_git


class TestTargetDirectoryStates:
    def test_no_target_dir_exists(
        self,
        cli_runner,
        service_path: Path,
        service_inputs_file: Path,
        service_vars_file: Path,
    ):
        result = cli_runner.invoke(
            create_no_git,
            ["--name", "acr_test", "--in-file", str(service_inputs_file.absolute())],
        )
        assert not result.exception
        assert (
            f"Service configuration files have been written to {service_path.joinpath('acr_test')}"
            in result.output
        )
        assert f"{service_path.joinpath('acr_test')} was created" in result.output
        assert "You will need to initialize it." in result.output
        assert (
            service_path.joinpath("acr_test").exists()
            and service_path.joinpath("acr_test").is_dir()
        )

    def test_target_dir_exists(
        self,
        cli_runner,
        service_path: Path,
        service_inputs_file: Path,
        service_vars_file: Path,
    ):
        service_path.joinpath("acr_test").mkdir(exist_ok=False)
        result = cli_runner.invoke(
            create_no_git,
            ["--name", "acr_test", "--in-file", str(service_inputs_file.absolute())],
        )
        assert not result.exception
        assert (
            f"Service configuration files have been written to {service_path.joinpath('acr_test')}"
            in result.output
        )
        assert f"{service_path.joinpath('acr_test')} already existed" in result.output
        assert "You will need to initialize it." in result.output
        assert (
            service_path.joinpath("acr_test").exists()
            and service_path.joinpath("acr_test").is_dir()
        )

    def test_target_dir_exists_with_git(
        self,
        cli_runner,
        service_path: Path,
        service_inputs_file: Path,
        service_vars_file: Path,
    ):
        service_path.joinpath("acr_test").mkdir(exist_ok=False)
        service_path.joinpath("acr_test").joinpath(".git").mkdir(exist_ok=False)
        result = cli_runner.invoke(
            create_no_git,
            ["--name", "acr_test", "--in-file", str(service_inputs_file.absolute())],
        )
        assert not result.exception
        assert (
            f"Service configuration files have been written to {service_path.joinpath('acr_test')}"
            in result.output
        )
        assert (
            f"{service_path.joinpath('acr_test')} appears to be a git repository! You will need to add, commit, and push these files manually."
            in result.output
        )
        assert (
            service_path.joinpath("acr_test").exists()
            and service_path.joinpath("acr_test").is_dir()
        )
