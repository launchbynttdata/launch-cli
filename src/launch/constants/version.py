from semver import Version

from launch.lib.common.utilities import read_toml_version

VERSION = read_toml_version()

SEMANTIC_VERSION = Version.parse(VERSION)


def read_toml_version():
    with open("./../../../pyproject.toml", "r") as file:
        lines = file.readlines()

    version = None
    for line in lines:
        if line.startswith("version"):
            version = line.split("=")[1].strip().strip('"')
            break

    return version
