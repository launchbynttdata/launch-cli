from pathlib import Path

import pytest

from launch.lib.service.test import functions as test_functions


def test_execute_test(mocker):
    service_dir = Path("/fake/dir")

    mock_os = mocker.patch.object(test_functions, "os")
    mock_git_config = mocker.patch.object(test_functions.functions, "git_config")
    mock_make_configure = mocker.patch.object(
        test_functions.functions, "make_configure"
    )
    mock_make_test = mocker.patch.object(test_functions.functions, "make_test")
    mock_subprocess = mocker.patch.object(test_functions.functions.subprocess, "run")
    mock_make_install = mocker.patch.object(test_functions.functions, "make_install")

    test_functions.execute_test(service_dir, dry_run=True)

    mock_subprocess.assert_not_called()
    mock_os.chdir.assert_called_once_with(service_dir)
    mock_git_config.assert_called_once_with(dry_run=True)
    mock_make_configure.assert_called_once_with(dry_run=True)
    mock_make_install.assert_called_once_with(dry_run=True)
    mock_make_test.assert_called_once_with(dry_run=True)
