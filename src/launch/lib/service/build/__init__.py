import os
from pathlib import Path

from launch.lib.automation.processes.functions import (
    git_config,
    make_build,
    make_configure,
    make_docker_aws_ecr_login,
    make_push,
    start_docker,
)


def execute_build(
    service_dir: Path,
    provider: str = "aws",
    push: bool = False,
    dry_run: bool = True,
) -> None:
    os.chdir(service_dir)
    start_docker(dry_run=dry_run)
    git_config(dry_run=dry_run)
    make_configure(dry_run=dry_run)
    make_build(dry_run=dry_run)

    if push:
        if provider == "aws":
            make_docker_aws_ecr_login(dry_run=dry_run)
        make_push(dry_run=dry_run)
