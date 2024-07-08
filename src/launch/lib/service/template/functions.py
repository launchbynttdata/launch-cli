import logging
import os
import re
import shutil
from fnmatch import fnmatch
from pathlib import Path
from typing import List
from uuid import uuid4

import click
from jinja2 import Environment, FileSystemLoader

from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

logger = logging.getLogger(__name__)


def process_template(
    src_base: Path,
    dest_base: Path,
    config: dict,
    parent_keys=[],
    skip_uuid=True,
    dry_run=True,
) -> None:
    """
    Recursively creates a directory structure and copies files based on a provided template.

    This function traverses a nested dictionary structure to create directories, updates paths to
    be relative to the destination base directory. It will also copy additional files
    based on specific keys defined in the structure.

    Args:
        src_base (Path): The base path of the source directory containing the template files.
        dest_base (Path): The base path of the destination directory where the new structure will be created.
        structure (dict): A nested dictionary structure defining the directory structure and files to copy.
        parent_keys (list, optional): The keys represent directory names, and the values can be nested dictionaries or strings.
        update_paths (bool, optional): A flag to indicate whether to update paths to be relative to the destination base directory.

    Returns:
        dict: A dictionary representing the updated configuration structure.
    """

    updated_config = {}
    for key, value in config.items():
        current_keys = parent_keys + [key]
        current_path = dest_base.joinpath(*current_keys)
        updated_config[key] = {}
        if isinstance(value, dict):
            if dry_run:
                click.secho(
                    f"[DRYRUN] Processing template, would have created dir: {current_path}",
                    fg="yellow",
                )
            else:
                current_path.mkdir(parents=True, exist_ok=True)

            if LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value in value:
                file_path = Path(
                    value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value]
                ).resolve()
                relative_path = current_path.joinpath(file_path.name)
                value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value] = str(
                    f"./{relative_path.relative_to(dest_base)}"
                )
                if dry_run:
                    click.secho(
                        f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                        fg="yellow",
                    )
                else:
                    shutil.copy(file_path, relative_path)
            if LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value in value:
                updated_files = []
                for file in value[LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value]:
                    file_path = Path(file).resolve()
                    relative_path = current_path.joinpath(file_path.name)
                    updated_files.append(str(relative_path.relative_to(dest_base)))
                    if dry_run:
                        click.secho(
                            f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                            fg="yellow",
                        )
                    else:
                        shutil.copy(file_path, relative_pcopy_and_render_templatesath)
            if LAUNCHCONFIG_KEYS.UUID.value in value and not skip_uuid:
                value[LAUNCHCONFIG_KEYS.UUID.value] = f"{str(uuid4())[:6]}"
            updated_config[key] = process_template(
                src_base=src_base,
                dest_base=dest_base,
                config=value,
                parent_keys=current_keys,
                skip_uuid=skip_uuid,
                dry_run=dry_run,
            )
        else:
            updated_config[key] = value

    return updated_config


def copy_template_files(
    src_dir: Path, target_dir: Path, exclude_dir: str, dry_run: bool = True
) -> None:
    """
    Copies files from a source directory to a target directory, excluding a specific directory.

    Args:
        src_dir (Path): The source directory containing the files to be copied.
        target_dir (Path): The target directory where the files will be copied.
        exclude_dir (str): The directory to exclude from the copy operation.

    Returns:
        None
    """
    if dry_run:
        click.secho(
            f"[DRYRUN] Processing template, would have copied files: {src_dir=} {target_dir=} {exclude_dir=}",
            fg="yellow",
        )
        return
    os.makedirs(target_dir, exist_ok=True)

    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        target_item = os.path.join(target_dir, item)
        if os.path.isdir(src_item):
            if item != exclude_dir and item != ".git":
                shutil.copytree(src_item, target_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, target_item)


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
    dry_run: bool = True,
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

    if dry_run:
        click.secho(
            f"[DRYRUN] Rending temlpate, would have rendered: {destination_path}",
            fg="yellow",
        )
    else:
        with open(destination_path, "w") as f:
            f.write(output)
        logger.info(f"Rendered template saved to {destination_path=}")


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
    base_dir: str,
    template_paths: list,
    modified_paths: list,
    context_data: dict = {},
    dry_run: bool = True,
) -> None:
    base_path = Path(base_dir)
    for template_path_str, modified_path in zip(template_paths, modified_paths):
        template_path = Path(template_path_str)
        file_name = template_path.name.replace(".j2", "")
        path_parts = modified_path.strip("/").split("/")
        dirs_to_render = find_dirs_to_render(base_path, path_parts[:-1])
        for dir_path in dirs_to_render:
            render_jinja_template(
                template_path=template_path,
                destination_dir=dir_path,
                file_name=file_name,
                template_data=context_data,
                dry_run=dry_run,
            )


def merge_templates(
    src_dir: Path,
    dest_dir: Path,
    dry_run: bool = True,
) -> None:
    for item in src_dir.iterdir():
        if item.is_dir():
            if "{{" in item.name and "}}" in item.name:
                for sub_dir in dest_dir.iterdir():
                    if sub_dir.is_dir:
                        merge_templates(item, sub_dir, dry_run)
            else:
                new_dest = dest_dir / item.name
                new_dest.mkdir(exist_ok=True, parents=True)
                merge_templates(item, new_dest, dry_run)
        else:
            if dry_run:
                click.secho(
                    f"[DRYRUN] Rending templates, would have copied: {item=} {item.name=}",
                    fg="yellow",
                )
            else:
                shutil.copy2(item, dest_dir / item.name)
