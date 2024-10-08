import pytest

from pathlib import Path
from launch.lib.service.build import functions as build_functions


@pytest.mark.parametrize("registry_type", ["npm", "docker"])
@pytest.mark.parametrize("push", [True, False])
def test_execute_build_no_push(mocker, capsys, registry_type, push):
    service_dir = Path("/fake/dir")

    mock_os = mocker.patch.object(build_functions, "os")
    mock_start_docker = mocker.patch.object(build_functions.functions, "start_docker")
    mock_git_config = mocker.patch.object(build_functions.functions, "git_config")
    mock_make_configure = mocker.patch.object(
        build_functions.functions, "make_configure"
    )
    mock_make_build = mocker.patch.object(build_functions.functions, "make_build")
    mock_make_docker_aws_ecr_login = mocker.patch.object(
        build_functions.functions, "make_docker_aws_ecr_login"
    )
    mock_make_push = mocker.patch.object(build_functions.functions, "make_push")
    mock_subprocess = mocker.patch.object(build_functions.functions.subprocess, "run")
    mock_make_install = mocker.patch.object(build_functions.functions, "make_install")

    build_functions.execute_build(
        service_dir=service_dir, registry_type=registry_type, push=True, dry_run=True
    )

    if registry_type == "docker":
        mock_start_docker.assert_called_once_with(dry_run=True)
        mock_make_install.assert_not_called()
        if push:
            mock_make_docker_aws_ecr_login.assert_called_once_with(dry_run=True)
            mock_make_push.assert_called_once_with(dry_run=True)
    elif registry_type == "npm":
        mock_start_docker.assert_not_called()
        mock_make_docker_aws_ecr_login.assert_not_called()
        mock_make_push.assert_not_called()
        mock_make_install.assert_called_once_with(dry_run=True)

    mock_subprocess.assert_not_called()
    mock_os.chdir.assert_called_once_with(service_dir)
    mock_git_config.assert_called_once_with(dry_run=True)
    mock_make_configure.assert_called_once_with(dry_run=True)
    mock_make_build.assert_called_once_with(dry_run=True)
