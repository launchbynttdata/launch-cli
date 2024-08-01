from semver import Version

from launch import __version__

VERSION = __version__

SEMANTIC_VERSION = Version.parse(VERSION)
