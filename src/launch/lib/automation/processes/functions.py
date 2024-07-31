import subprocess
import time

import click


def make_configure(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make configure")
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
    click.secho(f"Running make docker/build")
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
    click.secho(f"Running make docker/push")
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
    click.secho(f"Running make docker/aws_ecr_login")
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


def git_config(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make git config")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: git config",
                fg="yellow",
            )
        else:
            subprocess.run(
                ["git", "config", "--global", "user.name", "nobody"], check=True
            )
            subprocess.run(
                ["git", "config", "--global", "user.email", "nobody@nttdata.com"],
                check=True,
            )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def start_docker(
    dry_run: bool = True,
) -> None:
    click.secho(f"Starting docker if not running")
    try:
        if not is_docker_running():
            if dry_run:
                click.secho(
                    f"[DRYRUN] Would have started docker daemon",
                    fg="yellow",
                )
            else:
                subprocess.Popen(
                    ["dockerd"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=True,
                )
                time.sleep(5)  # Docker daemon takes a few seconds to start
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def is_docker_running() -> bool:
    try:
        subprocess.run(
            ["docker", "ps"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        click.secho(
            f"Docker found not to be running...",
            fg="yellow",
        )
        return False
