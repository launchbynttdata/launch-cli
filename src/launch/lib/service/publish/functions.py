import os
from pathlib import Path

import click

from launch.lib.automation.processes import functions


def execute_publish(
    service_dir: Path,
    registry_type: str,
    dry_run: bool = True,
    token_secret_name: str = None,
    package_scope: str = None,
    package_publisher: str = None,
    package_registry: str = None,
    source_folder_name: str = None,
    repo_path: str = None,
    source_branch: str = None,
) -> None:
    os.chdir(service_dir)
    functions.git_config(dry_run=dry_run)
    functions.make_configure(dry_run=dry_run)
    if registry_type == "npm":
        functions.make_install(dry_run=dry_run)
        functions.make_build(dry_run=dry_run)
        functions.make_publish(
            dry_run=dry_run,
            token_secret_name=token_secret_name,
            package_scope=package_scope,
            package_publisher=package_publisher,
            package_registry=package_registry,
            source_folder_name=source_folder_name,
            repo_path=repo_path,
            source_branch=source_branch,
        )
