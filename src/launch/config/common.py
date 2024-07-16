from launch.env import override_default

BUILD_DEPENDENCIES_PATH = override_default(
    key_name="BUILD_DEPENDENCIES_PATH", default=".launch"
)

BUILD_TEMP_DIR_PATH = override_default(
    key_name="BUILD_TEMP_DIR_PATH", default=f"{BUILD_DEPENDENCIES_PATH}/build"
)

PLATFORM_SRC_DIR_PATH = override_default(
    key_name="PLATFORM_SRC_DIR_PATH", default="platform"
)

TOOL_VERSION_FILE = override_default(
    key_name="TOOL_VERSION_FILE", default=".tool-versions"
)

SECRET_J2_TEMPLATE_NAME = override_default(
    key_name="SECRET_J2_TEMPLATE_NAME", default="secret.yaml"
)

NON_SECRET_J2_TEMPLATE_NAME = override_default(
    key_name="NON_SECRET_J2_TEMPLATE_NAME", default="non_secret.yaml"
)
