import os
import shutil
import subprocess
from pathlib import Path

import click

from launch.cli.j2.render import render
from launch.config.common import NON_SECRET_J2_TEMPLATE_NAME, SECRET_J2_TEMPLATE_NAME
from launch.config.terragrunt import TERRAGRUNT_RUN_DIRS
from launch.config.webhook import (
    WEBHOOK_BUILD_SCRIPT,
    WEBHOOK_GIT_REPO_TAG,
    WEBHOOK_GIT_REPO_URL,
    WEBHOOK_ZIP,
)
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS
from launch.lib.local_repo.repo import clone_repository


## Terragrunt Specific Functions
def terragrunt_init(run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt init subprocess in the current directory.

    Args:
        run_all (bool, optional): If set, it will run terragrunt init on all directories. Defaults to True.
        dry_run (bool, optional): If set, it will perform a dry run that reports on what it would do, but does not perform any action. Defaults to True.

    Raises:
        RuntimeError: If an error occurs during the subprocess.

    Returns:
        None
    """

    click.secho("Running terragrunt init")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "init",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = ["terragrunt", "init", "--terragrunt-non-interactive"]

    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: {subprocess_args=}",
                fg="yellow",
            )
        else:
            subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_plan(out_file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt plan subprocess in the current directory.

    Args:
        out_file (str, optional): The output file from running terragrunt plan. Defaults to None.
        run_all (bool, optional): If set, it will run terragrunt plan on all directories. Defaults to True.
        dry_run (bool, optional): If set, it will perform a dry run that reports on what it would do, but does not perform any action. Defaults to True.

    Raises:
        RuntimeError: If an error occurs during the subprocess.

    Returns:
        None
    """
    click.secho("Running terragrunt plan")
    if run_all:
        subprocess_args = ["terragrunt", "run-all", "plan"]
    else:
        subprocess_args = ["terragrunt", "plan"]

    if out_file:
        subprocess_args.append("-out")
        subprocess_args.append(out_file)
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: {subprocess_args=}",
                fg="yellow",
            )
        else:
            subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_apply(var_file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt apply subprocess in the current directory.

    Args:
        var_file (str, optional): The var file with inputs to pass to terragrunt. Defaults to None.
        run_all (bool, optional): If set, it will run terragrunt apply on all directories. Defaults to True.
        dry_run (bool, optional): If set, it will perform a dry run that reports on what it would do, but does not perform any action. Defaults to True.

    Raises:
        RuntimeError: If an error occurs during the subprocess.

    Returns:
        None
    """
    click.secho("Running terragrunt apply")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = [
            "terragrunt",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]

    if var_file:
        subprocess_args.append("-var-file")
        subprocess_args.append(var_file)
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: {subprocess_args=}",
                fg="yellow",
            )
        else:
            subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_destroy(var_file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt destroy subprocess in the current directory.

    Args:
        var_file (str, optional): The var file with inputs to pass to terragrunt. Defaults to None.
        run_all (bool, optional): If set, it will run terragrunt destroy on all directories. Defaults to True.
        dry_run (bool, optional): If set, it will perform a dry run that reports on what it would do, but does not perform any action. Defaults to True.

    Raises:
        RuntimeError: If an error occurs during the subprocess.
    """
    click.secho("Running terragrunt destroy")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "destroy",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = [
            "terragrunt",
            "destroy",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]

    if var_file:
        subprocess_args.append("-var-file")
        subprocess_args.append(var_file)
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have ran subprocess: {subprocess_args=}",
                fg="yellow",
            )
        else:
            subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def find_app_templates(
    context: click.Context,
    base_dir: Path,
    template_dir: Path,
    aws_profile: str,
    aws_region: str,
    dry_run: bool,
) -> None:
    """
    Finds app templates in the base_dir and processes them.

    Args:
        context (click.Context): The click context.
        base_dir (Path): The base directory to search for app templates.
        template_dir (Path): The directory where the templates are located.
        aws_profile (str): The AWS profile to use.
        aws_region (str): The AWS region to use.
        dry_run (bool): If set, it will perform a dry run that reports on what it would do, but does not perform any action.

    Returns:
        None
    """
    for instance_path, dirs, files in os.walk(base_dir):
        if LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value in dirs:
            process_app_templates(
                context=context,
                instance_path=instance_path,
                properties_path=Path(instance_path).joinpath(
                    LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value
                ),
                template_dir=template_dir,
                aws_profile=aws_profile,
                aws_region=aws_region,
                dry_run=dry_run,
            )


def process_app_templates(
    context: click.Context,
    instance_path: Path,
    properties_path: Path,
    template_dir: Path,
    aws_profile: str,
    aws_region: str,
    dry_run: bool,
) -> None:
    """
    Processes app templates in the properties_path. It will render the secret and non-secret templates for each
    application running the render command on them.

    Args:
        context (click.Context): The click context.
        instance_path (Path): The instance path.
        properties_path (Path): The properties path.
        template_dir (Path): The template directory.
        aws_profile (str): The AWS profile to use.
        aws_region (str): The AWS region to use.
        dry_run (bool): If set, it will perform a dry run that reports on what it would do, but does not perform any action.

    Returns:
        None
    """
    for file_name in os.listdir(properties_path):
        file_path = Path(properties_path).joinpath(file_name)
        folder_name = file_name.split(".")[0]
        secret_template = template_dir.joinpath(
            Path(f"{folder_name}/{SECRET_J2_TEMPLATE_NAME}")
        )
        non_secret_template = template_dir.joinpath(
            Path(f"{folder_name}/{NON_SECRET_J2_TEMPLATE_NAME}")
        )
        if secret_template.exists():
            context.invoke(
                render,
                values=file_path,
                template=secret_template,
                out_file=f"{instance_path}/{folder_name}.secret.auto.tfvars",
                type="secret",
                aws_secrets_profile=aws_profile,
                aws_secrets_region=aws_region,
                dry_run=dry_run,
            )
        if non_secret_template.exists():
            context.invoke(
                render,
                values=file_path,
                template=non_secret_template,
                out_file=f"{instance_path}/{folder_name}.non-secret.auto.tfvars",
                aws_secrets_profile=aws_profile,
                aws_secrets_region=aws_region,
                dry_run=dry_run,
            )


def copy_webhook(
    webhooks_path: str,
    build_path: str,
    target_environment: str,
    dry_run: bool = True,
) -> None:
    clone_repository(
        repository_url=WEBHOOK_GIT_REPO_URL,
        target=webhooks_path,
        branch=WEBHOOK_GIT_REPO_TAG,
        dry_run=dry_run,
    )
    cur_dir = Path.cwd()
    os.chdir(webhooks_path)
    os.chmod(webhooks_path.joinpath(WEBHOOK_BUILD_SCRIPT), 0o755)
    subprocess.run([webhooks_path.joinpath(WEBHOOK_BUILD_SCRIPT)], check=True)
    os.chdir(cur_dir)
    for root, dirs, files in os.walk(
        build_path.joinpath(TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment))
    ):
        relative_depth = len(
            os.path.relpath(
                root,
                build_path.joinpath(
                    TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment)
                ),
            ).split(os.sep)
        )
        if relative_depth == 2:
            shutil.copy(webhooks_path.joinpath(WEBHOOK_ZIP), root)
            print(f"Copied {webhooks_path.joinpath(WEBHOOK_BUILD_SCRIPT)} to {root}")
