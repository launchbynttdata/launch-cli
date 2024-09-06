import logging
import os
import subprocess
from pathlib import Path

import click

from launch.config.aws import AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE
from launch.config.common import TOOL_VERSION_FILE
from launch.config.github import GIT_MACHINE_USER, GIT_SCM_ENDPOINT

logger = logging.getLogger(__name__)


def parse_plugin_line(line: str) -> tuple[str, str, str | None]:
    split_line = line.split()
    plugin_name = split_line[0]
    plugin_version = split_line[1]
    plugin_url = (
        split_line[-1].strip("#").strip()
        if split_line[-1].strip("#").startswith("http")
        else None
    )
    return plugin_name, plugin_version, plugin_url


def install_tool_versions(file: str = TOOL_VERSION_FILE) -> None:
    logger.info("Installing all asdf plugins under .tool-versions")
    try:
        with open(file, "r") as fh:
            lines = fh.readlines()

        for line in lines:
            line = line.strip()
            if line:
                plugin_name, _, plugin_url = parse_plugin_line(line)
                if plugin_url:
                    subprocess.run(["asdf", "plugin", "add", plugin_name, plugin_url])
                else:
                    subprocess.run(["asdf", "plugin", "add", plugin_name])

        subprocess.run(["asdf", "install"])
    except Exception as e:
        raise RuntimeError(
            f"An error occurred with asdf install {file}: {str(e)}"
        ) from e


def set_netrc(
    password: str,
    machine: str = GIT_SCM_ENDPOINT,
    login: str = GIT_MACHINE_USER,
    netrc_path=Path.home().joinpath(".netrc"),
    dry_run: bool = True,
) -> None:
    click.secho(f"Setting {netrc_path} variables")
    if netrc_path.exists():
        click.secho(
            f"{netrc_path} already exists, skipping...",
            fg="yellow",
        )
        return
    try:
        if dry_run:
            click.secho(
                f"[DRYRUN] Would have written to {netrc_path}: {machine=} {login=}",
                fg="yellow",
            )
        else:
            with open(netrc_path, "a") as file:
                file.write(f"machine {machine}\n")
                file.write(f"login {login}\n")
                file.write(f"password {password}\n")

            os.chmod(netrc_path, 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


# This can be deprecated when we refactor the lambdas and no longer use shell scipts in the build process
def readFile(key, file_path=AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE) -> str:
    try:
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith(f"export {key}="):
                    value = line.split("=")[1].strip().strip('"')
                    return value
        return None
    except FileNotFoundError:
        click.secho(f"The file {file_path} does not exist.")
        return None
