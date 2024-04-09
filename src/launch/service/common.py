import json
import logging
import re
import shutil
import uuid
from pathlib import Path
from typing import List

from git.repo import Repo
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from launch import BUILD_DEPENDENCIES_DIR, SERVICE_SKELETON, SKELETON_BRANCH
from launch.automation.common.functions import (
    extract_uuid_key,
    recursive_dictionary_merge,
)

logger = logging.getLogger(__name__)


def callback_create_directories(
    key,
    value,
    **kwargs,
) -> bool:
    if isinstance(value, dict):
        next_path = Path(kwargs["base_path"]) / kwargs["current_path"] / Path(key)
        next_path.mkdir(parents=True, exist_ok=True)
        return False
    else:
        next_path = Path(kwargs["base_path"]) / kwargs["current_path"]
        next_path.mkdir(parents=True, exist_ok=True)

    return True


def callback_copy_properties_files(
    key,
    value,
    **kwargs,
) -> bool:
    if isinstance(value, dict):
        return None
    elif key == "properties_file":
        dest_path = kwargs["base_path"] / kwargs["current_path"]
        dest_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Copying {kwargs.get('base_path')}/{value} to {dest_path}")
        shutil.copy(
            kwargs["base_path"] / Path(value), dest_path / Path("terraform.tfvars")
        )

        relative_path = str(dest_path).removeprefix(kwargs["base_path"])
        kwargs["nested_dict"][
            key
        ] = f"{BUILD_DEPENDENCIES_DIR}/{relative_path}/terraform.tfvars"
    elif key == "uuid":
        kwargs["nested_dict"]["uuid"] = value
    if kwargs.get("uuid", False):
        kwargs["nested_dict"]["uuid"] = f"{str(uuid.uuid4())[:6]}"

    return kwargs["nested_dict"]


def list_jinja_templates(base_dir: str) -> tuple:
    base_path = Path(base_dir)
    template_paths = []
    modified_paths = []
    pattern = re.compile(r"\{\{.*?\}\}")

    for jinja_file in base_path.rglob("*.j2"):
        modified_path = pattern.sub("*", str(jinja_file))
        modified_path = modified_path.replace(str(base_path), "")
        modified_path = modified_path.lstrip("/")
        modified_paths.append(modified_path)
        template_paths.append(jinja_file.as_posix())

    return template_paths, modified_paths


def render_jinja_template(
    template_path: Path,
    destination_dir: str,
    file_name: str,
    template_data: dict = {"data": None},
) -> None:
    if not template_data.get("data"):
        template_data["data"] = {}

    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    template_data["data"]["path"] = str(destination_dir)
    template_data["data"]["config"]["dir_dict"] = get_value_by_path(
        template_data["data"]["config"]["platform"],
        str(destination_dir)[(str(destination_dir).find("platform") + 9) :],
    )
    output = template.render(template_data)
    destination_path = destination_dir / file_name

    with open(destination_path, "w") as f:
        f.write(output)
    logger.info(f"Rendered template saved to {destination_path}")


def create_specific_path(base_path: Path, path_parts: list) -> list:
    specific_path = base_path.joinpath(*path_parts)
    specific_path.mkdir(parents=True, exist_ok=True)
    return [specific_path]


def get_value_by_path(data: dict, path: str) -> dict:
    keys = path.split("/")
    val = data
    for key in keys:
        if isinstance(val, dict):
            val = val.get(key)
        else:
            return None
    return val


def expand_wildcards(
    current_path: Path,
    remaining_parts: List[str],
) -> List[Path]:
    """Expand wildcard paths."""
    if not remaining_parts:
        return [current_path]

    next_part, *next_remaining_parts = remaining_parts
    if next_part == "*":
        if not next_remaining_parts:
            return list_directories(current_path)
        else:
            all_subdirs = []
            for sub_path in list_directories(current_path):
                all_subdirs.extend(expand_wildcards(sub_path, next_remaining_parts))
            return all_subdirs
    else:
        next_path = current_path / next_part
        next_path.mkdir(exist_ok=True)
        return expand_wildcards(next_path, next_remaining_parts)


def list_directories(directory: Path) -> List[Path]:
    """List subdirectories in a given directory."""
    return [sub_path for sub_path in directory.iterdir() if sub_path.is_dir()]


def find_dirs_to_render(base_path: str, path_parts: list) -> list:
    base_path_obj = Path(base_path)
    if "*" not in path_parts:
        return create_specific_path(base_path_obj, path_parts)
    else:
        return expand_wildcards(base_path_obj, path_parts)


def copy_and_render_templates(
    base_dir: str, template_paths: list, modified_paths: list, context_data: dict = {}
) -> None:
    base_path = Path(base_dir)
    for template_path_str, modified_path in zip(template_paths, modified_paths):
        template_path = Path(template_path_str)
        file_name = template_path.name.replace(".j2", "")
        path_parts = modified_path.strip("/").split("/")
        dirs_to_render = find_dirs_to_render(base_path, path_parts[:-1])
        for dir_path in dirs_to_render:
            render_jinja_template(template_path, dir_path, file_name, context_data)


def write_text(
    path: Path, data: dict, output_format: str = "json", indent: int = 4
) -> None:
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


def determine_existing_uuid(input_data: dict, repository: Repo) -> dict:
    launch_config_path = Path(repository.working_dir).joinpath(".launch_config")
    launch_config = json.loads(launch_config_path.read_text())
    platform_config = launch_config["platform"]
    uuid_dict = extract_uuid_key(platform_config)
    recursive_dictionary_merge(input_data, uuid_dict)
    return input_data
