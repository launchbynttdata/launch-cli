from launch.env import override_default

BUILD_DEPENDENCIES_DIR = override_default(
    key_name="BUILD_DEPENDENCIES_DIR", default="./.launch"
)
BUILD_TEMP_DIR_PATH = override_default(
    key_name="BUILD_TEMP_DIR_PATH", default=f"{BUILD_DEPENDENCIES_DIR}/build"
)
CODE_GENERATION_DIR_SUFFIX = override_default(
    key_name="CODE_GENERATION_DIR_SUFFIX", default="-singleRun"
)
PLATFORM_SRC_DIR_PATH = override_default(
    key_name="PLATFORM_SRC_DIR_PATH", default="platform"
)
