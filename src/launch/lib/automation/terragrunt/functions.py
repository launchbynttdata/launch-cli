import json
import logging
import os
import subprocess
from pathlib import Path

import click

from launch.config.terragrunt import TERRAGRUNT_RUN_DIRS
from launch.lib.automation.environment.functions import install_tool_versions, set_netrc
from launch.lib.automation.provider.aws.functions import assume_role

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
    logger.info("Running terragrunt init")
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
                f"[DRYRUN] Would have ran subprocess {subprocess_args=}",
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
    logger.info("Running terragrunt plan")
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
                f"[DRYRUN] Would have ran subprocess {subprocess_args=}",
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
    logger.info("Running terragrunt apply")
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
                f"[DRYRUN] Would have ran subprocess {subprocess_args=}",
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
    logger.info("Running terragrunt destroy")
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
                f"[DRYRUN] Would have ran subprocess {subprocess_args=}",
                fg="yellow",
            )
        else:
            subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def prepare_for_terragrunt(
    target_environment: str,
    provider_config: dict,
    platform_resource: str,
    skip_diff: bool,
) -> dict[Path]:
    """
    Prepares the environment for running terragrunt commands.

    Args:
        target_environment (str): The target environment to run the terragrunt command against.
        provider_config (dict): Provider config as a string used for any specific config needed for certain providers.
        platform_resource (str): If set, this will set the specified pipeline resource to run terragrunt against.
        skip_diff (bool): If set, it will ignore checking the diff between the pipeline and service changes.

    Raises:
        FileNotFoundError: If the path does not exist.

    Returns:
        dict[Path]: The directories to run terragrunt in.
    """

    install_tool_versions()
    set_netrc()

    # If the Provider is AZURE there is a prequisite requirement of logging into azure
    # i.e. az login, or service principal is already applied to the environment.
    # If the provider is AWS, we need to assume the role for deployment.
    provider = provider_config["provider"]
    if provider_config:
        if provider == "aws":
            assume_role(provider_config=provider_config)

    if platform_resource == "all":
        run_dirs = [
            TERRAGRUNT_RUN_DIRS["service"].joinpath(target_environment),
            TERRAGRUNT_RUN_DIRS["pipeline"].joinpath(target_environment),
            TERRAGRUNT_RUN_DIRS["webhook"].joinpath(target_environment),
        ]
    elif platform_resource in TERRAGRUNT_RUN_DIRS:
        run_dirs = [TERRAGRUNT_RUN_DIRS[platform_resource].joinpath(target_environment)]

    for run_dir in run_dirs:
        if not (run_dir).exists():
            message = f"Error: Path {run_dir.joinpath(run_dir)} does not exist."
            click.secho(message, fg="red")
            raise FileNotFoundError(message)

    return run_dirs
