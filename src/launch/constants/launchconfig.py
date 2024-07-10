from pathlib import Path

LAUNCHCONFIG_NAME = ".launch_config"
LAUNCHCONFIG_PATH_LOCAL = Path(f"./{LAUNCHCONFIG_NAME}")
LAUNCHCONFIG_HOME_LOCAL = Path.home().joinpath(LAUNCHCONFIG_NAME)
