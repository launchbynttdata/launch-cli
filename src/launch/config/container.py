import time

from launch.env import override_default

CONTAINER_IMAGE_NAME = override_default(key_name="CONTAINER_IMAGE_NAME", default=None)

DEFAULT_CONTAINER_TAG = override_default(
    key_name="DEFAULT_CONTAINER_TAG",
    default=f"{int(time.time())}-dev",
)

CONTAINER_IMAGE_VERSION = override_default(
    key_name="CONTAINER_IMAGE_VERSION", default=DEFAULT_CONTAINER_TAG
)

CONTAINER_REGISTRY = override_default(key_name="CONTAINER_REGISTRY", default=None)
