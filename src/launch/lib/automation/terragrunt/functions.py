import logging
import os
import subprocess
from pathlib import Path

import click

from launch.cli.j2.render import render
from launch.config.common import NON_SECRET_J2_TEMPLATE_NAME, SECRET_J2_TEMPLATE_NAME
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

logger = logging.getLogger(__name__)


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


def terragrunt_plan(file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt plan subprocess in the current directory.

    Args:
        file (str, optional): The file to pass to terragrunt. Defaults to None.
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

    if file:
        subprocess_args.append("-out")
        subprocess_args.append(file)
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


def terragrunt_apply(file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt apply subprocess in the current directory.

    Args:
        file (str, optional): The file to pass to terragrunt. Defaults to None.
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

    if file:
        subprocess_args.append("-var-file")
        subprocess_args.append(file)
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


def terragrunt_destroy(file=None, run_all=True, dry_run=True) -> None:
    """
    Runs terragrunt destroy subprocess in the current directory.

    Args:
        file (str, optional): The file to pass to terragrunt. Defaults to None.
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

    if file:
        subprocess_args.append("-var-file")
        subprocess_args.append(file)
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
    context: click.Context, base_dir: Path, template_dir: Path, dry_run: bool
) -> None:
    for instance_path, dirs, files in os.walk(base_dir):
        if LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value in dirs:
            process_app_templates(
                context=context,
                instance_path=instance_path,
                properties_path=Path(instance_path).joinpath(
                    LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value
                ),
                template_dir=template_dir,
                dry_run=dry_run,
            )


def process_app_templates(
    context: click.Context,
    instance_path: Path,
    properties_path: Path,
    template_dir: Path,
    dry_run: bool,
) -> None:
    for file_name in os.listdir(properties_path):
        file_path = Path(properties_path).joinpath(file_name)
        folder_name = file_name.split(".")[0]
        secret_template = template_dir.joinpath(
            Path(f"{folder_name}/{SECRET_J2_TEMPLATE_NAME}")
        )
        non_secret_template = template_dir.joinpath(
            Path(f"{folder_name}/{NON_SECRET_J2_TEMPLATE_NAME}")
        )
        # if secret_template.exists():
        #     context.invoke(
        #         render,
        #         values=file_path,
        #         template=secret_template,
        #         out_file=f"{instance_path}/{folder_name}.secret.auto.tfvars",
        #         dry_run=dry_run,
        #     )
        logger.info(f"non Secret Template: {non_secret_template}")
        if non_secret_template.exists():
            context.invoke(
                render,
                values=file_path,
                template=non_secret_template,
                out_file=f"{instance_path}/{folder_name}.non-secret.auto.tfvars",
                dry_run=dry_run,
            )
