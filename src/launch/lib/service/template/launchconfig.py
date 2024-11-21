import logging
import os
import shutil
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

import click

from launch.config.terraform import TERRAFORM_VAR_FILE
from launch.enums.launchconfig import LAUNCHCONFIG_KEYS

logger = logging.getLogger(__name__)


class LaunchConfigTemplate:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def properties_file(self, value: dict, current_path: Path, dest_base: Path) -> None:
        file_path = Path(value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value]).resolve()
        relative_path = current_path.joinpath(file_path.name)
        value[LAUNCHCONFIG_KEYS.PROPERTIES_FILE.value] = str(
            f"./{relative_path.relative_to(dest_base).with_name(TERRAFORM_VAR_FILE)}"
        )
        if self.dry_run:
            click.secho(
                f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                fg="yellow",
            )
        else:
            with suppress(shutil.SameFileError):
                shutil.copy(file_path, relative_path.with_name(TERRAFORM_VAR_FILE))

    def copy_additional_files(
        self, value: dict, current_path: Path, dest_base: Path
    ) -> None:
        for target_file, source_file in value[
            LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value
        ].items():
            file_path = Path(source_file).resolve()
            target_path = current_path.joinpath(target_file)
            value[LAUNCHCONFIG_KEYS.ADDITIONAL_FILES.value][target_file] = str(
                f"./{target_path.relative_to(dest_base)}"
            )
            
            if self.dry_run:
                click.secho(
                    f"[DRYRUN] Processing template, would have copied: {file_path} to {target_path}",
                    fg="yellow",
                )
            else:
                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_path, target_path)
                except shutil.SameFileError:
                    pass

    def templates(self, value: dict, current_path: Path, dest_base: Path) -> None:
        for name, templates in value[LAUNCHCONFIG_KEYS.TEMPLATES.value].items():
            logger.info(f"{templates=}")
            for type, file in templates.items():
                file_path = Path(file).resolve()
                relative_path = current_path.joinpath(
                    f"{LAUNCHCONFIG_KEYS.TEMPLATES.value}/{name}/{type}.yaml"
                )
                value[LAUNCHCONFIG_KEYS.TEMPLATES.value][name][type] = str(
                    f"./{relative_path.relative_to(dest_base)}"
                )
                if self.dry_run:
                    click.secho(
                        f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                        fg="yellow",
                    )
                else:
                    os.makedirs(
                        current_path.joinpath(
                            f"{LAUNCHCONFIG_KEYS.TEMPLATES.value}/{name}"
                        ),
                        exist_ok=True,
                    )
                    try:
                        shutil.copy(file_path, relative_path)
                    except shutil.SameFileError:
                        pass

    def template_properties(
        self,
        value: dict,
        current_path: Path,
        dest_base: Path,
    ) -> None:
        for name, file in value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value].items():
            file_path = Path(file).resolve()
            relative_path = current_path.joinpath(
                f"{LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value}/{name}.yaml"
            )
            value[LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value][name] = str(
                f"./{relative_path.relative_to(dest_base)}"
            )
            if self.dry_run:
                click.secho(
                    f"[DRYRUN] Processing template, would have copied: {file_path} to {relative_path}",
                    fg="yellow",
                )
            else:
                os.makedirs(
                    current_path.joinpath(
                        f"{LAUNCHCONFIG_KEYS.TEMPLATE_PROPERTIES.value}"
                    ),
                    exist_ok=True,
                )
                try:
                    shutil.copy(file_path, relative_path)
                except shutil.SameFileError:
                    pass

    def uuid(
        self,
        value: dict
    ) -> None:
        if LAUNCHCONFIG_KEYS.UUID.value not in value:
            value[LAUNCHCONFIG_KEYS.UUID.value] = f"{str(uuid4())[:6]}"

    def get_provider(self, resource: str, input_data: dict) -> str:
        if isinstance(input_data[LAUNCHCONFIG_KEYS.PROVIDER.value], dict):
            if resource in input_data[LAUNCHCONFIG_KEYS.PROVIDER.value]:
                return input_data[LAUNCHCONFIG_KEYS.PROVIDER.value][resource]
            else:
                return input_data[LAUNCHCONFIG_KEYS.PROVIDER.value]["service"]
        else:
            return input_data[LAUNCHCONFIG_KEYS.PROVIDER.value]
