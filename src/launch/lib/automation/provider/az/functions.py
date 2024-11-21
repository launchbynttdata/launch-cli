import logging
import re
import os
import subprocess
import click
from pathlib import Path

from launch.lib.automation.processes.functions import make_configure

logger = logging.getLogger(__name__)


def deploy_remote_state(
    uuid_value: str,
    naming_prefix: str,
    target_environment: str,
    region: str,
    instance: str,
    build_path: Path,
    dry_run: bool = False,
) -> None:
    run_list = ["make"]

    make_configure(dry_run=dry_run)
 
    stripped_name = re.sub("[\W_]+", "", naming_prefix)
    storage_account_name = f"{stripped_name[0:16]}{uuid_value}"
    if naming_prefix:
        run_list.append(f"NAME_PREFIX={naming_prefix}")
    if region:
        run_list.append(f"REGION={region}")
    if target_environment:
        run_list.append(f"ENVIRONMENT={target_environment}")
    if instance:
        run_list.append(f"ENV_INSTANCE={instance}")

    run_list.append(f"STORAGE_ACCOUNT_NAME={storage_account_name}")
    run_list.append("terragrunt/remote_state/azure")

    logger.info(f"Running {run_list}")
    try:
        subprocess.run(run_list, check=True, cwd=build_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
