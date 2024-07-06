import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4

import click

from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

logger = logging.getLogger(__name__)


def process_template(
    src_base: Path,
    dest_base: Path,
    config: dict,
    parent_keys=[],
    copy_jinja=False,
    skip_uuid=True,
    dry_run=True,
) -> None:
    """
    Recursively creates a directory structure and copies files based on a provided template.

    This function traverses a nested dictionary structure to create directories, updates paths to
    be relative to the destination base directory, and optionally copy '.j2' template files from
    a source base directory to a destination base directory. It will also copy additional files
    based on specific keys defined in the structure.

    Args:
        src_base (Path): The base path of the source directory containing the template files.
        dest_base (Path): The base path of the destination directory where the new structure will be created.
        structure (dict): A nested dictionary structure defining the directory structure and files to copy.
        parent_keys (list, optional): The keys represent directory names, and the values can be nested dictionaries or strings.
        copy_jinja (bool, optional): A flag to indicate whether to copy '.j2' template files.
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
                        shutil.copy(file_path, relative_path)
            if LAUNCHCONFIG_KEYS.UUID.value in value and not skip_uuid:
                value[LAUNCHCONFIG_KEYS.UUID.value] = f"{str(uuid4())[:6]}"
            updated_config[key] = process_template(
                src_base=src_base,
                dest_base=dest_base,
                config=value,
                parent_keys=current_keys,
                copy_jinja=copy_jinja,
                skip_uuid=skip_uuid,
                dry_run=dry_run,
            )
        else:
            updated_config[key] = value

        if copy_jinja:
            src_folder = src_base.joinpath(*parent_keys)
            for file in src_folder.glob(f"*j2"):
                dest_file_path = src_base.joinpath(*parent_keys)
                if dry_run:
                    click.secho(
                        f"[DRYRUN] Processing template, would have copied: {file} to {dest_file_path}",
                        fg="yellow",
                    )
                else:
                    shutil.copy(file, dest_file_path)

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
