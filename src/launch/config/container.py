from launch.env import override_default
from launch.lib.automation.environment.functions import readFile

CONTAINER_IMAGE_NAME = override_default(
    key_name="CONTAINER_IMAGE_NAME",
    default=None,
)

CONTAINER_IMAGE_VERSION = override_default(
    key_name="CONTAINER_IMAGE_VERSION",
    default=readFile("CONTAINER_IMAGE_VERSION"),
)

CONTAINER_REGISTRY = override_default(
    key_name="CONTAINER_REGISTRY",
    default=None,
)
