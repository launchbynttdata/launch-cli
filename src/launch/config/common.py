from launch.env import override_default

AWS_REGION = override_default(key_name="AWS_REGION", default="us-east-2")

BUILD_DEPENDENCIES_DIR = override_default(
    key_name="BUILD_DEPENDENCIES_DIR", default=".launch"
)
BUILD_TEMP_DIR_PATH = override_default(
    key_name="BUILD_TEMP_DIR_PATH", default=f"{BUILD_DEPENDENCIES_DIR}/build"
)
PLATFORM_SRC_DIR_PATH = override_default(
    key_name="PLATFORM_SRC_DIR_PATH", default="platform"
)
