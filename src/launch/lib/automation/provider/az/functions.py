import logging
import re
import subprocess
from typing import Union

logger = logging.getLogger(__name__)


def deploy_remote_state(
    uuid_value: str,
    naming_prefix: str,
    target_environment: str,
    region: str,
    instance: str,
    provider_config: dict,
) -> None:
    run_list = ["make"]
    provider = provider_config["provider"]

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

    if provider in provider_config:
        if "container_name" in provider_config[provider]:
            run_list.append(
                f"CONTAINER_NAME={provider_config[provider].get('container_name')}"
            )
        if "storage_account_name" in provider_config[provider]:
            storage_account_name = provider_config[provider].get("storage_account_name")
        if provider_config[provider].get("resource_group_name"):
            run_list.append(
                f"RESOURCE_GROUP_NAME={provider_config[provider].get('resource_group_name')}"
            )

    run_list.append(f"STORAGE_ACCOUNT_NAME={storage_account_name}")
    run_list.append("terragrunt/remote_state/azure")

    logger.info(f"Running {run_list}")
    try:
        subprocess.run(run_list, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
