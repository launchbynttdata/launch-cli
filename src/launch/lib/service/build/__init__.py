import os
from pathlib import Path

from launch.config.common import DOCKER_FILE_NAME
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.lib.automation.processes.functions import (
    git_config,
    make_configure,
    make_docker_aws_ecr_login,
    make_docker_build,
    make_docker_push,
    start_docker,
)
from launch.lib.local_repo.repo import clone_repository, checkout_branch


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
    make_docker_build(dry_run=dry_run)

    if push:
        if provider == "aws":
            make_docker_aws_ecr_login(dry_run=dry_run)
        make_docker_push(dry_run=dry_run)


def clone_if_no_dockerfile(
    url: str,
    tag: str,
    service_dir: Path,
    clone_dir: Path,
    dry_run: bool = False,
) -> Path:
    if not service_dir.joinpath(DOCKER_FILE_NAME).exists():
        repository = clone_repository(
            repository_url=url,
            target=clone_dir,
            branch=SERVICE_MAIN_BRANCH,
            dry_run=dry_run,
        )
        checkout_branch(
            repository=repository,
            target_branch=tag,
            dry_run=dry_run,
        )
        return clone_dir
