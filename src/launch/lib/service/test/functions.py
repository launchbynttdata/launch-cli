import os
from pathlib import Path

from launch.lib.automation.processes import functions


def execute_test(
    service_dir: Path,
    dry_run: bool = True,
) -> None:
    os.chdir(service_dir)
    functions.git_config(dry_run=dry_run)
    functions.make_configure(dry_run=dry_run)
    functions.make_install(dry_run=dry_run)
    functions.make_test(dry_run=dry_run)
