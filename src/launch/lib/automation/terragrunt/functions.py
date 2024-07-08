import json
import logging
import os
import subprocess
from pathlib import Path

from git import Repo

from launch.constants.common import BUILD_DEPENDENCIES_DIR, CODE_GENERATION_DIR_SUFFIX
from launch.lib.automation.common.functions import (
    install_tool_versions,
    make_configure,
    set_netrc,
    traverse_with_callback,
)
from launch.lib.automation.provider.aws.functions import assume_role
from launch.lib.automation.provider.az.functions import callback_deploy_remote_state

logger = logging.getLogger(__name__)


## Terragrunt Specific Functions
def terragrunt_init(run_all=True):
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
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_plan(file=None, run_all=True):
    logger.info("Running terragrunt plan")
    if run_all:
        subprocess_args = ["terragrunt", "run-all", "plan"]
    else:
        subprocess_args = ["terragrunt", "plan"]

    if file:
        subprocess_args.append("-out")
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_apply(file=None, run_all=True):
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
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_destroy(file=None, run_all=True):
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
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


# This logic is used to get everything ready for terragrunt. This includes:
# 1. Cloning the repository
# 2. Checking out the commit sha
# 3. Installing all asdf plugins under .tool-versions
# 4. Setting ~/.netrc variables
# 5. Copying files and directories from the properties repository to the terragrunt directory
# 6. Assuming the role if the provider is AWS
# 7. Changing the directory to the terragrunt directory
def prepare_for_terragrunt(
    repository: Repo,
    name: str,
    git_token: str,
    commit_sha: str,
    target_environment: str,
    provider_config: dict,
    skip_diff: bool,
    pipeline_resource: str,
    path: str,
    override: dict,
):
    os.chdir(f"{path}/{name}{CODE_GENERATION_DIR_SUFFIX}")
    with open(f"{path}/{name}{CODE_GENERATION_DIR_SUFFIX}/.launch_config", "r") as f:
        launch_config = json.load(f)

    install_tool_versions(
        file=override["tool_versions_file"],
    )
    set_netrc(password=git_token, machine=override["machine"], login=override["login"])

    # If the Provider is AZURE there is a prequisite requirement of logging into azure
    # i.e. az login, or service principal is already applied to the environment.
    # If the provider is AWS, we need to assume the role for deployment.
    provider = provider_config["provider"]
    if provider_config:
        if provider == "aws":
            assume_role(
                provider_config=provider_config,
                repository_name=name,
                target_environment=target_environment,
            )
        if provider.startswith("az"):
            make_configure()
            traverse_with_callback(
                dictionary=launch_config["platform"],
                callback=callback_deploy_remote_state,
                base_path=f"{path}/{name}{CODE_GENERATION_DIR_SUFFIX}/{BUILD_DEPENDENCIES_DIR}/",
                naming_prefix=launch_config["naming_prefix"],
                target_environment=target_environment,
                provider_config=provider_config,
            )

    if pipeline_resource:
        exec_dir = Path(
            f"{override['infrastructure_dir']}/{pipeline_resource}-{provider}/{target_environment}"
        )
    else:
        exec_dir = Path(f"{override['environment_dir']}/{target_environment}")

    if not (exec_dir).exists():
        message = f"Error: Path {exec_dir} does not exist."
        logger.error(message)
        raise FileNotFoundError(message)

    os.chdir(exec_dir)
