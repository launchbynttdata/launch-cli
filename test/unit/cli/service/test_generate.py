from pathlib import Path

from launch.constants.common import CODE_GENERATION_DIR_SUFFIX
from launch.cli.service.commands import generate


def test_generate(cli_runner, initialized_repo: Path, fake_module_git_url):
    service_path = initialized_repo
    result = cli_runner.invoke(generate, ["--name", "acr_test", "--skip-git"])
    assert not result.exception

    singlerun_path = service_path.joinpath(f"acr_test{CODE_GENERATION_DIR_SUFFIX}")
    assert singlerun_path.exists() and singlerun_path.is_dir()

    platform_path = singlerun_path.joinpath("platform")
    assert platform_path.exists() and platform_path.is_dir()

    makefile_path = singlerun_path.joinpath("Makefile")
    assert makefile_path.exists() and makefile_path.is_file()

    service_hcl_path = (
        platform_path.joinpath("service")
        .joinpath("tf-configuration")
        .joinpath("service.hcl")
    )
    assert service_hcl_path.exists() and service_hcl_path.is_file()

    service_hcl_contents = service_hcl_path.read_text()
    assert fake_module_git_url in service_hcl_contents
