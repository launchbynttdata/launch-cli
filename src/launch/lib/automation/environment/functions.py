import logging
import os
import subprocess
from pathlib import Path

import click

from launch.config.common import TOOL_VERSION_FILE
from launch.config.github import GIT_MACHINE_USER, GIT_SCM_ENDPOINT

logger = logging.getLogger(__name__)


def install_tool_versions(file: str = TOOL_VERSION_FILE) -> None:
    logger.info("Installing all asdf plugins under .tool-versions")
    try:
        with open(file, "r") as file:
            lines = file.readlines()

        for line in lines:
            plugin = line.split()[0]
            subprocess.run(["asdf", "plugin", "add", plugin])

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
def set_vars_from_bash_Var_file(file_path: str) -> None:
    """ """
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("export"):
                    key_value = line[len("export ") :].split("=", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        value = value.strip('"')
                        os.environ[key] = value
    except Exception as e:
        raise RuntimeError(
            f"An error occurred while setting environment variables: {str(e)}"
        )
