import os
import click
from pathlib import Path

from launch.lib.automation.processes import functions


def execute_build(
    service_dir: Path,
    registry_type: str,
    provider: str,
    push: bool = False,
    dry_run: bool = True,
) -> None:
    os.chdir(service_dir)
    if registry_type == "docker":
        functions.start_docker(dry_run=dry_run)

    functions.git_config(dry_run=dry_run)
    functions.make_configure(dry_run=dry_run)

    if registry_type == "npm":
        functions.make_install(dry_run=dry_run)

    functions.make_build(dry_run=dry_run)

    if push:
        if registry_type == "docker":
            if provider == "aws":
                functions.make_docker_aws_ecr_login(dry_run=dry_run)
            functions.make_push(dry_run=dry_run)
