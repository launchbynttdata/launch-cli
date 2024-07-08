import json
import pathlib
from typing import Generator

import pytest


@pytest.fixture
def isolated_helm_chart_with_dependencies(
    tmp_path,
) -> Generator[pathlib.Path, None, None]:
    source_file = pathlib.Path(__file__).parent.joinpath("data/simple_chart.yaml")
    destination_file = tmp_path.joinpath("Chart.yaml")
    destination_file.write_text(source_file.read_text())
    yield destination_file


@pytest.fixture
def helm_directory(tmp_path):
    return pathlib.Path(tmp_path)


@pytest.fixture
def top_level_chart(helm_directory):
    chart_file = helm_directory.joinpath("Chart.yaml")
    chart_file.touch()
    return chart_file


@pytest.fixture
def remote_dependencies() -> list[dict[str, str]]:
    return [
        {
            "name": "dependency1",
            "version": "1.0.0",
            "repository": "https://foo.com/helm-repo/charts/",
        },
        {
            "name": "dependency2",
            "version": "2.0.0",
            "repository": "https://foo.com/helm-repo/charts/",
        },
    ]


@pytest.fixture
def local_dependencies() -> list[dict[str, str]]:
    return [
        {
            "name": "dependency1",
            "version": "1.0.0",
            "repository": "file://../../charts/dependency1",
        },
        {
            "name": "dependency2",
            "version": "2.0.0",
            "repository": "file://../../charts/dependency2",
        },
    ]


@pytest.fixture
def mixed_dependencies() -> list[dict[str, str]]:
    return [
        {
            "name": "dependency1",
            "version": "1.0.0",
            "repository": "https://foo.com/helm-repo/charts/",
        },
        {
            "name": "dependency2",
            "version": "2.0.0",
            "repository": "file://../../charts/dependency2",
        },
    ]


@pytest.fixture
def empty_dependencies() -> list[dict[str, str]]:
    return []


@pytest.fixture
def eq_global_dependencies() -> dict[str, str]:
    return {"dependency1": "1.0.0", "dependency2": "2.0.0"}


@pytest.fixture
def conflict_global_dependencies() -> dict[str, str]:
    return {"dependency1": "0.5.0", "dependency2": "2.0.0"}


@pytest.fixture
def empty_global_dependencies() -> dict[str, str]:
    return {}


@pytest.fixture
def simple_chart_no_deps() -> dict[str, str]:
    return {
        "apiVersion": "v2",
        "name": "umbrella-chart",
        "description": "Consumes the deployment-chart and creates a generic deployment",
        "type": "application",
        "version": "0.0.1",
        "appVersion": "0.0.1",
        "dependencies": [],
    }


@pytest.fixture
def chartfile_no_deps(
    simple_chart_no_deps,
    helm_directory,
):
    chart_file = helm_directory.joinpath("Chart.yaml")
    json.dump(simple_chart_no_deps, open(chart_file, "w"))
    return chart_file


@pytest.fixture
def chartfile_local_deps(
    simple_chart_no_deps,
    helm_directory,
    local_dependencies,
):
    simple_chart_no_deps["dependencies"] = local_dependencies
    chart_file = helm_directory.joinpath("Chart.yaml")
    chart_file.write_text(json.dumps(simple_chart_no_deps))
    return chart_file


@pytest.fixture
def chartfile_remote_deps(
    simple_chart_no_deps,
    helm_directory,
    remote_dependencies,
):
    simple_chart_no_deps["dependencies"] = remote_dependencies
    chart_file = helm_directory.joinpath("Chart.yaml")
    chart_file.write_text(json.dumps(simple_chart_no_deps))
    return chart_file


@pytest.fixture
def chartfile_mixed_deps(
    simple_chart_no_deps,
    helm_directory,
    mixed_dependencies,
):
    simple_chart_no_deps["dependencies"] = mixed_dependencies
    chart_file = helm_directory.joinpath("Chart.yaml")
    chart_file.write_text(json.dumps(simple_chart_no_deps))
    return chart_file
