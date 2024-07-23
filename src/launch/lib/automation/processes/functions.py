import logging
import subprocess

import click

logger = logging.getLogger(__name__)


def make_configure(
    dry_run: bool = True,
) -> None:
    logger.info(f"Running make configure")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make configure",
                fg="yellow",
            )
        else:
            subprocess.run(["make", "configure"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_docker_build(
    dry_run: bool = True,
) -> None:
    logger.info(f"Running make docker/build")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make docker/build",
                fg="yellow",
            )
        else:
            subprocess.run(["make", "docker/build"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_docker_push(
    dry_run: bool = True,
) -> None:
    logger.info(f"Running make docker/push")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make docker/push",
                fg="yellow",
            )
        else:
            subprocess.run(["make", "docker/push"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_docker_aws_ecr_login(
    dry_run: bool = True,
) -> None:
    logger.info(f"Running make docker/aws_ecr_login")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make docker/aws_ecr_login",
                fg="yellow",
            )
        else:
            subprocess.run(["make", "docker/aws_ecr_login"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
