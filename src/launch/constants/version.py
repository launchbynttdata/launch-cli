from importlib.metadata import version 
from semver import Version


VERSION = version('launch-cli')

SEMANTIC_VERSION = Version.parse(VERSION)
