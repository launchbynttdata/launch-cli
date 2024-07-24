import json
import os
from pathlib import Path

from launch.constants.launchconfig import (
    LAUNCHCONFIG_HOME_LOCAL,
    LAUNCHCONFIG_PATH_LOCAL,
)


def strtobool(value: str) -> bool:
    """Turns a truthy or falsy case-insensitive string into a boolean. Previously this was provided by distutils, but that has been deprecated.

    Args:
        value (str): Input value to turn into a boolean.

    Raises:
        ValueError: Raised if the input string isn't one of our recognized truthy or falsy values.

    Returns:
        bool: Result of determining truthiness or falsiness.
    """
    value = str(value)
    truthy_values = ["y", "yes", "t", "true", "on", "1"]
    falsy_values = ["n", "no", "f", "false", "off", "0"]
    if value.lower() in truthy_values:
        return True
    elif value.lower() in falsy_values:
        return False
    else:
        raise ValueError(
            f"Provided string '{value}' was not valid! Must be one of {truthy_values + falsy_values}"
        )


def get_bool_env_var(env_var_name: str, default_value: bool) -> bool:
    """Gets a value from an environment variable if it is set, and returns the default_value otherwise.

    Args:
        env_var_name (str): Name of the environment variable to pull from.
        default_value (bool): Replacement value if the environment variable is not set.

    Raises:
        ValueError: Raises from internal comparison if the value in the environment variable isn't one of our recognized truthy or falsy values.

    Returns:
        bool: Result of determining truthiness or falsiness.
    """
    return strtobool(os.environ.get(env_var_name, default=default_value))


def override_default(
    key_name: str,
    default: str = None,
    required: bool = False,
) -> str:
    """
    Override the default value of a key in the launchconfig file. It will first check if the key is present in the environment
    variables. If it is present, it will return the value of the key. If it is not present, it will check the local launchconfig
    file to see if the key is present in the override section. If it is not present, it will check the global launchconfig file.
    If the key is not present in either file, it will return the default value.

    Args:
        key_name (str): The string key name to override
        default (str): The default value of the key

    Returns:
        str: The value of the key in the launchconfig file or the default value
    """
    if os.environ.get(key_name):
        return os.environ.get(key_name)

    if Path(LAUNCHCONFIG_PATH_LOCAL).exists():
        with open(LAUNCHCONFIG_PATH_LOCAL, "r") as f:
            local_config = json.load(f)
            if "override" in local_config:
                if key_name in local_config["override"]:
                    return local_config["override"][key_name]

    if Path(os.path.expanduser(LAUNCHCONFIG_HOME_LOCAL)).exists():
        with open(os.path.expanduser(LAUNCHCONFIG_HOME_LOCAL), "r") as f:
            global_config = json.load(f)
            if key_name in global_config["override"]:
                return global_config["override"][key_name]

    if required and default is None:
        raise RuntimeError(
            f"ERROR: The {key_name} environment variable is not set. You must set this environment variable before running this command."
        )
    else:
        return default


UPDATE_CHECK = get_bool_env_var("LAUNCH_CLI_UPDATE_CHECK", False)
UPDATE_ALLOW_PRERELEASE = get_bool_env_var("LAUNCH_CLI_UPDATE_ALLOW_PRERELEASE", False)
