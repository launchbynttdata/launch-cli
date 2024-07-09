import json
import logging
from pathlib import Path

import click
from ruamel.yaml import YAML

from launch.config.launchconfig import SERVICE_SKELETON, SKELETON_BRANCH
from launch.constants.launchconfig import LAUNCHCONFIG_NAME
from launch.lib.common.utilities import extract_uuid_key, recursive_dictionary_merge

logger = logging.getLogger(__name__)


def write_text(
    path: Path,
    data: dict,
    output_format: str = "json",
    indent: int = 4,
    dry_run: bool = False,
) -> None:
    if dry_run:
        click.secho(
            f"[DRYRUN] Would have written data: {path=} {output_format=} {indent=} {data=}",
            fg="yellow",
        )
        return

    if output_format == "json":
        serialized_data = json.dumps(data, indent=indent)
        path.write_text(serialized_data)
    elif output_format == "yaml":
        yaml = YAML()
        yaml.dump(data=data, stream=path)
    else:
        message = f"Unsupported output format: {output_format}"
        logger.error(message)
        raise ValueError(message)


def input_data_validation(input_data: dict) -> dict:
    if not "skeleton" in input_data:
        input_data["skeleton"]: dict[str, str] = {}
    if not "url" in input_data["skeleton"] or not input_data["skeleton"]["url"]:
        logger.info(f"No skeleton url provided, using default: {SERVICE_SKELETON}")
        input_data["skeleton"]["url"] = SERVICE_SKELETON
    if not "tag" in input_data["skeleton"] or not input_data["skeleton"]["tag"]:
        logger.info(f"No skeleton tag provided, using default: {SKELETON_BRANCH}")
        input_data["skeleton"]["tag"] = SKELETON_BRANCH

    return input_data


def determine_existing_uuid(
    input_data: dict,
    path: Path,
    force: bool = False,
) -> dict:
    launch_config_path = Path(path).joinpath(LAUNCHCONFIG_NAME)

    if not launch_config_path.exists() and not force:
        click.secho(
            f"No {LAUNCHCONFIG_NAME} found in local directory. Use --force to recreate when running this command.",
            fg="red",
        )
        quit()
    elif launch_config_path.exists() and force:
        launch_config = json.loads(launch_config_path.read_text())
        uuid_dict = extract_uuid_key(launch_config["platform"])
        input_data = recursive_dictionary_merge(input_data, uuid_dict["platform"])

    return input_data
