import logging
import subprocess
from test.unit.lib.automation.helm.fixtures import (
    chartfile_local_deps,
    chartfile_mixed_deps,
    chartfile_no_deps,
    chartfile_remote_deps,
    conflict_global_dependencies,
    empty_dependencies,
    empty_global_dependencies,
    eq_global_dependencies,
    helm_directory,
    local_dependencies,
    mixed_dependencies,
    remote_dependencies,
    simple_chart_no_deps,
    top_level_chart,
)
from unittest import mock

import pytest

from launch.lib.automation.helm.functions import (
    add_dependency_repositories,
    extract_dependencies_from_chart,
    resolve_dependencies,
    resolve_next_layer_dependencies,
)


def helm_add_repo_call(dependencies: list[dict[str, str]]):
    helm_add_repo_calls = []
    for dep in dependencies:
        if not dep["repository"].startswith("file://"):
            this_call = mock.Mock()
            this_call.call_args = mock.call(
                ["helm", "repo", "add", dep["name"], dep["repository"]]
            )
            helm_add_repo_calls.append(this_call.call_args)
    return helm_add_repo_calls


def helm_dep_archives_from_dependencies(dependencies: list[dict[str, str]]):
    helm_dep_archives = []
    for dep in dependencies:
        helm_dep_archives.append(
            f"/mock/path/to/dependency/{dep['name']}-{dep['version']}.tgz"
        )
    return helm_dep_archives


def test_extract_dependencies_none(
    chartfile_no_deps,
):
    extracted_dependencies = extract_dependencies_from_chart(chartfile_no_deps)
    assert len(extracted_dependencies) == 0


def test_extract_dependencies_mixed(chartfile_mixed_deps, mixed_dependencies):
    extracted_dependencies = extract_dependencies_from_chart(chartfile_mixed_deps)
    assert len(extracted_dependencies) == len(mixed_dependencies)
    assert extracted_dependencies == mixed_dependencies


def test_resolve_dependencies_raises_error_if_no_chart_yaml(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_dependencies(
            helm_directory=tmp_path, global_dependencies={}, dry_run=False
        )


def test_add_remote_dependency_repositories(mocker, remote_dependencies):
    mocker.patch("subprocess.call")
    dependencies = remote_dependencies
    helm_call = helm_add_repo_call(dependencies)
    add_dependency_repositories(dependencies)
    assert subprocess.call.mock_calls == helm_call


def test_add_mixed_dependency_repositories(mocker, mixed_dependencies):
    mocker.patch("subprocess.call")
    dependencies = mixed_dependencies
    helm_call = helm_add_repo_call(dependencies)
    add_dependency_repositories(dependencies)
    assert subprocess.call.mock_calls == helm_call


def test_add_dependency_repositories_local_dependency(mocker, local_dependencies):
    mocker.patch("subprocess.call")
    dependencies = local_dependencies
    add_dependency_repositories(dependencies)
    subprocess.call.assert_not_called()


def test_resolve_next_layer_dependencies_empty_dependencies(
    mocker, caplog, empty_dependencies, helm_directory, empty_global_dependencies
):
    mock_discover_files = mocker.patch(
        "launch.lib.automation.helm.functions.discover_files"
    )
    global_dependencies = empty_global_dependencies
    dependencies = empty_dependencies
    dependency_archives = helm_dep_archives_from_dependencies(dependencies)
    mock_discover_files.return_value = dependency_archives
    with caplog.at_level(logging.DEBUG):
        resolve_next_layer_dependencies(
            dependencies, helm_directory, global_dependencies, dry_run=False
        )
    assert len(caplog.records) > 0
    assert f"Found {len(dependency_archives)} archives." not in caplog.text
    assert f"Inspecting {len(dependencies)} dependencies" in caplog.text
    mock_discover_files.assert_not_called()


def test_resolve_next_layer_dependencies_mixed_dependencies(
    mocker, caplog, mixed_dependencies, helm_directory, empty_global_dependencies
):
    # Create our list of mock archive paths
    dependency_archives = helm_dep_archives_from_dependencies(mixed_dependencies)

    # Create mock objects of the associated functions
    mock_resolve_dependencies = mocker.patch(
        "launch.lib.automation.helm.functions.resolve_dependencies"
    )
    mock_discover_files = mocker.patch(
        "launch.lib.automation.helm.functions.discover_files"
    )
    mock_unpack_archive = mocker.patch(
        "launch.lib.automation.helm.functions.unpack_archive"
    )

    # Set up our test
    global_dependencies = empty_global_dependencies
    dependencies = mixed_dependencies
    mock_discover_files.return_value = dependency_archives
    mock_unpack_archive.return_value = True
    mock_resolve_dependencies.return_value = None

    with caplog.at_level(logging.DEBUG):
        resolve_next_layer_dependencies(
            dependencies, helm_directory, global_dependencies, dry_run=False
        )
    assert len(caplog.records) > 0
    assert f"Found {len(dependency_archives)} archives." in caplog.text
    assert f"Inspecting {len(dependencies)} dependencies" in caplog.text


def test_resolve_dependencies_empty_global_empty_deps(
    mocker, caplog, empty_dependencies, helm_directory, empty_global_dependencies
):
    dependencies = empty_dependencies
    global_dependencies = empty_global_dependencies

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "launch.lib.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "launch.lib.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "launch.lib.automation.helm.functions.resolve_next_layer_dependencies"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_chart_exists.return_value = True
    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None
    with caplog.at_level(logging.DEBUG):
        resolve_dependencies(helm_directory, global_dependencies, dry_run=False)
    assert f"Found {len(dependencies)} dependencies" in caplog.text
    assert len(caplog.records) > 0
    for record in caplog.records:
        assert record.levelname != "EXCEPTION"
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)


def test_resolve_dependencies_empty_global_mixed_deps(
    mocker, caplog, mixed_dependencies, helm_directory, empty_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = empty_global_dependencies

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "launch.lib.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "launch.lib.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "launch.lib.automation.helm.functions.resolve_next_layer_dependencies"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None
    with caplog.at_level(logging.DEBUG):
        resolve_dependencies(helm_directory, global_dependencies, dry_run=False)
    assert len(caplog.records) > 0
    assert f"Found {len(dependencies)} dependencies" in caplog.text
    assert "already known" not in caplog.text
    for record in caplog.records:
        assert record.levelname != "EXCEPTION"
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)


def test_resolve_dependencies_eq_global_mixed_deps(
    mocker, caplog, mixed_dependencies, helm_directory, eq_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = eq_global_dependencies

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "launch.lib.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "launch.lib.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "launch.lib.automation.helm.functions.resolve_next_layer_dependencies"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None
    with caplog.at_level(logging.DEBUG):
        resolve_dependencies(helm_directory, global_dependencies, dry_run=False)
    assert len(caplog.records) > 0
    assert f"Found {len(dependencies)} dependencies" in caplog.text
    assert "already known" in caplog.text
    for record in caplog.records:
        assert record.levelname != "EXCEPTION"
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)


def test_resolve_dependencies_conflict_global_mixed_deps(
    mocker, caplog, mixed_dependencies, helm_directory, conflict_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = conflict_global_dependencies

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "launch.lib.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "launch.lib.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "launch.lib.automation.helm.functions.resolve_next_layer_dependencies"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(RuntimeError, match="conflicting versions"):
            resolve_dependencies(helm_directory, global_dependencies, dry_run=False)
    assert len(caplog.records) > 0
    assert f"Found {len(dependencies)} dependencies" in caplog.text
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)
