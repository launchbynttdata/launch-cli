import os
from pathlib import Path

from launch.env import override_default
from launch.config.common import DEFAULT_CONTAINER_TAG, DOCKER_FILE_NAME
from launch.config.launchconfig import SERVICE_MAIN_BRANCH
from launch.lib.automation.provider.aws.functions import assume_role
from launch.lib.automation.processes.functions import (
    make_configure,
    make_docker_aws_ecr_login,
    make_docker_build,
    make_docker_push,
)
from launch.lib.local_repo.repo import clone_repository, checkout_branch


def execute_build(
    service_dir: Path,
    provider: str = "aws",
    push: bool = False,
    dry_run: bool = True,
) -> None:
    os.chdir(service_dir)
    make_configure(dry_run=dry_run)
    make_docker_build(dry_run=dry_run)

    if push:
        if provider == "aws":
            make_docker_aws_ecr_login(dry_run=dry_run)
        os.environ["CONTAINER_IMAGE_VERSION"] = override_default(
            key_name="MERGE_COMMIT_ID", default=DEFAULT_CONTAINER_TAG
        )
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
