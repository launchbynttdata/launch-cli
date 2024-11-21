import os
import subprocess
import time

import click

from launch.lib.github.generate_github_token import get_secret_value
from launch.lib.local_repo.predict import predict_version
from launch.lib.local_repo.tags import read_semantic_tags

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


def make_build(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make build")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make build",
                fg="yellow",
            )
        else:
            env = os.environ.copy()
            subprocess.run(["make", "build"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_install(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make install")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make install",
                fg="yellow",
            )
        else:
            env = os.environ.copy()
            subprocess.run(["make", "install"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_test(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make test")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make test",
                fg="yellow",
            )
        else:
            env = os.environ.copy()
            subprocess.run(["make", "test"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_push(
    dry_run: bool = True,
) -> None:
    click.secho(f"Running make push")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make push",
                fg="yellow",
            )
        else:
            env = os.environ.copy()
            subprocess.run(["make", "push"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def make_publish(
    dry_run: bool = True,
    token_secret_name: str = None,
    package_scope: str = None,
    package_publisher: str = None,
    package_registry: str = None,
    source_folder_name: str = None,
    repo_path: str = None,
    source_branch: str = None,
) -> None:
    click.secho(f"Running make publish")
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: make publish",
                fg="yellow",
            )
        else:
            if token_secret_name is not None:
                token = get_secret_value(token_secret_name)

                # Predict the tag
                predicted_version = predict_version(
                    existing_tags=read_semantic_tags(repo_path=repo_path),
                    branch_name=source_branch,
                )
                click.echo(f"predicted_version is: {predicted_version}")
                # Update package.json to reflect new version
                subprocess.run(f"make version TAG={predicted_version}", shell=True, check=True)
                # NPM login
                subprocess.run(["make", "login", f"PACKAGE_REGISTRY={package_registry}", f"PACKAGE_PUBLISHER={package_publisher}", f"PACKAGE_SCOPE={package_scope}", f"TOKEN={token}"], check=True)
                # Publish to npm registry
                subprocess.run(["make", "publish"], check=True)
            else:
                click.secho(
                    f"Valid PAT token must be provided to publish to npm registry", fg="red",
                )
                quit()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e

# Move to AWS Provider. 
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
