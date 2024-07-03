import logging
import pathlib
import subprocess

from launch.lib.automation.common.functions import (
    discover_files,
    load_yaml,
    unpack_archive,
)

logger = logging.getLogger(__name__)


def resolve_dependencies(
    helm_directory: pathlib.Path, global_dependencies: dict[str, str], dry_run: bool
) -> None:
    """Recursive function to resolve Helm dependencies based on Chart.yaml file in provided path.

    Args:
        helm_directory (pathlib.Path): Directory containing a Chart.yaml file.

    Raises:
        FileNotFoundError: If no Chart.yaml is found in the provided directory.
    """
    top_level_chart = helm_directory.joinpath("Chart.yaml")
    logger.debug(f"Looking for Chart.yaml in {helm_directory}")
    if not top_level_chart.exists():
        fnf_message = f"No Chart.yaml found in {helm_directory}"
        logger.debug(fnf_message)
        raise FileNotFoundError(fnf_message)

    dependencies = extract_dependencies_from_chart(chart_file=top_level_chart)
    logger.debug(f"Found {len(dependencies)} dependencies in {helm_directory}")

    for dependency in dependencies:
        if dependency["name"] not in global_dependencies:
            global_dependencies[dependency["name"]] = dependency["version"]
            logger.debug(
                f"Remembering dependency {dependency['name']} with version {dependency['version']}."
            )
        elif global_dependencies[dependency["name"]] != dependency["version"]:
            conflict_message = (
                f"Dependency {dependency['name']} has conflicting versions: "
                f"{global_dependencies[dependency['name']]} and {dependency['version']}. "
                "You must resolve this conflict before continuing."
            )
            logger.exception(conflict_message)
            raise RuntimeError(conflict_message)
        else:
            logger.debug(
                f"Dependency {dependency['name']} already known with version {dependency['version']}."
            )
    if not dry_run:
        add_dependency_repositories(dependencies)

        subprocess.call(["helm", "dep", "build", "."], cwd=helm_directory)

        resolve_next_layer_dependencies(
            dependencies, helm_directory, global_dependencies, dry_run=dry_run
        )
    else:
        logger.info("Dry run requested, skipping dependency recursion.")


def extract_dependencies_from_chart(chart_file: pathlib.Path) -> list[dict[str, str]]:
    """Loads a Chart file and returns the contents of the 'dependencies' section.

    Args:
        chart_file (pathlib.Path): Path to a Helm Chart.yaml

    Returns:
        list[dict[str, str]]: A list of dependency objects, or an empty list if there are no dependencies.
    """
    yaml_contents = load_yaml(yaml_file=chart_file)
    dependencies = yaml_contents.get("dependencies", [])
    logger.debug(
        f"Loaded {len(dependencies)} dependencies from the chart at {chart_file}"
    )

    return dependencies


def add_dependency_repositories(dependencies: list[dict[str, str]]) -> None:
    """Adds Helm repositories for each dependency in the provided list.

    Args:
        dependencies (list[dict[str, str]]): A list of dependency objects.
    """
    for dependency in dependencies:
        if dependency["repository"].startswith("file://"):
            # Local dependency, no need to fetch
            continue
        else:
            logger.debug(
                f"Running: helm repo add {dependency['name']} {dependency['repository']}"
            )
            subprocess.call(
                ["helm", "repo", "add", dependency["name"], dependency["repository"]]
            )


def resolve_next_layer_dependencies(
    dependencies: list[dict[str, str]],
    helm_directory: pathlib.Path,
    global_dependencies: dict[str, str],
    dry_run: bool,
) -> None:
    """Inspect any dependencies of the provided dependencies and resolve them.

    Args:
        dependencies (list[dict[str, str]]): A list of dependency objects.
        helm_directory (pathlib.Path): Directory containing a Chart.yaml file.
    """
    logger.debug(
        f"Inspecting {len(dependencies)} dependencies for further dependencies."
    )
    for dependency in dependencies:
        # Discover the dependency archives -- there should be one for each version, but only ever one version included as a dependency.
        dependency_archives = discover_files(
            helm_directory.joinpath("charts"), filename_partial=dependency["name"]
        )
        logger.debug(f"Found {len(dependency_archives)} archives.")

        for dependency_archive in dependency_archives:
            logger.debug(
                f"Unpacking {dependency_archive} to {helm_directory.joinpath('charts')}".strip()
            )
            unpack_archive(dependency_archive, helm_directory.joinpath("charts"))
            resolve_dependencies(
                helm_directory.joinpath(f"charts/{dependency['name']}"),
                global_dependencies,
                dry_run=dry_run,
            )
