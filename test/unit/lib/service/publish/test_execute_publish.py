from pathlib import Path

import pytest

from launch.lib.service.publish import functions as publish_functions


@pytest.mark.parametrize("registry_type", ["npm"])
def test_execute_publish(mocker, registry_type):
    service_dir = Path("/fake/dir")

    mock_os = mocker.patch.object(publish_functions, "os")
    mock_git_config = mocker.patch.object(publish_functions.functions, "git_config")
    mock_make_configure = mocker.patch.object(
        publish_functions.functions, "make_configure"
    )
    mock_make_build = mocker.patch.object(publish_functions.functions, "make_build")
    mock_make_install = mocker.patch.object(publish_functions.functions, "make_install")
    mock_make_publish = mocker.patch.object(publish_functions.functions, "make_publish")

    publish_functions.execute_publish(
        service_dir=service_dir,
        registry_type=registry_type,
        dry_run=True,
    )

    if registry_type == "npm":
        mock_make_install.assert_called_once_with(dry_run=True)
        mock_make_build.assert_called_once_with(dry_run=True)
        mock_make_publish.assert_called_once_with(
            dry_run=True,
            token_secret_name=None,
            package_scope=None,
            package_publisher=None,
            package_registry=None,
            source_folder_name=None,
            repo_path=None,
            source_branch=None,
        )

    mock_os.chdir.assert_called_once_with(service_dir)
    mock_git_config.assert_called_once_with(dry_run=True)
    mock_make_configure.assert_called_once_with(dry_run=True)
