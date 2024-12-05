import pathlib
from unittest import mock

import pytest

from launch.lib.automation.helm.functions import (
    check_release_existence,
    install_chart,
    run_deployment,
    template_chart,
    update_chart,
)


# Helper functions
def setup_mocks(mocker, release_exists=False):
    mock_check_release_existence = mocker.patch(
        "launch.lib.automation.helm.functions.check_release_existence",
        return_value=release_exists,
    )
    mock_install_chart = mocker.patch(
        "launch.lib.automation.helm.functions.install_chart"
    )
    mock_update_chart = mocker.patch(
        "launch.lib.automation.helm.functions.update_chart"
    )
    return mock_check_release_existence, mock_install_chart, mock_update_chart


def get_common_parameters():
    helm_directory = pathlib.Path("/mock/path/to/chart")
    release_name = "test-release"
    namespace = "test-namespace"
    return helm_directory, release_name, namespace


# Test functions
def test_run_deployment_dry_run(mocker):
    mock_check_release_existence, mock_install_chart, mock_update_chart = setup_mocks(
        mocker, release_exists=False
    )
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = True

    run_deployment(helm_directory, release_name, namespace, dry_run)

    mock_check_release_existence.assert_called_once_with(release_name, namespace)
    mock_install_chart.assert_called_once_with(
        helm_directory, release_name, namespace, dry_run
    )
    mock_update_chart.assert_not_called()


def test_run_deployment_update(mocker):
    mock_check_release_existence, mock_install_chart, mock_update_chart = setup_mocks(
        mocker, release_exists=True
    )
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = False

    run_deployment(helm_directory, release_name, namespace, dry_run)

    mock_check_release_existence.assert_called_once_with(release_name, namespace)
    mock_update_chart.assert_called_once_with(
        helm_directory, release_name, namespace, dry_run
    )
    mock_install_chart.assert_not_called()


def test_check_release_existence(mocker):
    mock_check_output = mocker.patch("subprocess.check_output")
    release_name = "test-release"
    namespace = "test-namespace"

    # Test when the release exists
    mock_check_output.return_value = "test-release\nanother-release"
    result = check_release_existence(release_name, namespace)
    mock_check_output.assert_called_once_with(
        ["helm", "list", "--namespace", namespace, "--short", "--deployed"],
        universal_newlines=True,
    )
    assert result is True

    # Reset mock for the next test
    mock_check_output.reset_mock()

    # Test when the release does not exist
    mock_check_output.return_value = "another-release"
    result = check_release_existence(release_name, namespace)
    mock_check_output.assert_called_once_with(
        ["helm", "list", "--namespace", namespace, "--short", "--deployed"],
        universal_newlines=True,
    )
    assert result is False


def test_install_chart(mocker):
    mock_subprocess_call = mocker.patch("subprocess.call")
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = False

    install_chart(helm_directory, release_name, namespace, dry_run)

    mock_subprocess_call.assert_called_once_with(
        ["helm", "install", release_name, helm_directory, "--namespace", namespace]
    )


def test_install_chart_dry_run(mocker):
    mock_subprocess_call = mocker.patch("subprocess.call")
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = True

    install_chart(helm_directory, release_name, namespace, dry_run)

    mock_subprocess_call.assert_called_once_with(
        [
            "helm",
            "install",
            release_name,
            helm_directory,
            "--namespace",
            namespace,
            "--dry-run",
        ]
    )


def test_update_chart(mocker):
    mock_subprocess_call = mocker.patch("subprocess.call")
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = False

    update_chart(helm_directory, release_name, namespace, dry_run)

    mock_subprocess_call.assert_called_once_with(
        ["helm", "upgrade", release_name, helm_directory, "--namespace", namespace]
    )


def test_update_chart_dry_run(mocker):
    mock_subprocess_call = mocker.patch("subprocess.call")
    helm_directory, release_name, namespace = get_common_parameters()
    dry_run = True

    update_chart(helm_directory, release_name, namespace, dry_run)

    mock_subprocess_call.assert_called_once_with(
        [
            "helm",
            "upgrade",
            release_name,
            helm_directory,
            "--namespace",
            namespace,
            "--dry-run",
        ]
    )


def test_template_chart(mocker):
    mock_check_output = mocker.patch("subprocess.check_output")
    helm_directory, release_name, namespace = get_common_parameters()
    expected_output = "mocked output"

    mock_check_output.return_value = expected_output

    output = template_chart(helm_directory, release_name, namespace)

    mock_check_output.assert_called_once_with(
        ["helm", "template", release_name, helm_directory, "--namespace", namespace],
        universal_newlines=True,
    )
    assert output == expected_output
