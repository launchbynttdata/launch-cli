from launch.env import override_default

CONTAINER_IMAGE_NAME = override_default(
    key_name="CONTAINER_IMAGE_NAME",
    default=None,
)

CONTAINER_IMAGE_VERSION = override_default(
    key_name="CONTAINER_IMAGE_VERSION",
    default=None,
)

CONTAINER_REGISTRY = override_default(
    key_name="CONTAINER_REGISTRY",
    default=None,
)
