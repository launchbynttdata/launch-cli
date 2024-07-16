from pathlib import Path

from launch.config.common import PLATFORM_SRC_DIR_PATH
from launch.env import override_default

TERRAGRUNT_RUN_DIRS = {
    "service": Path(f"{PLATFORM_SRC_DIR_PATH}/service"),
    "pipeline": Path(f"{PLATFORM_SRC_DIR_PATH}/pipeline/pipeline-provider"),
    "webhook": Path(f"{PLATFORM_SRC_DIR_PATH}/pipeline/webhook-provider"),
}

TARGETENV = override_default(
    key_name="TARGETENV",
    default="sandbox",
)

PLATFORM_ENV = override_default(
    key_name="TARGETENV",
    default="root",
)
