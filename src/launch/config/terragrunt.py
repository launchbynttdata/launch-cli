from pathlib import Path

from launch.env import override_default

TERRAGRUNT_RUN_DIRS = {
    "service": Path("platform/service"),
    "pipeline": Path("platform/pipeline/pipeline-provider"),
    "webhook": Path("platform/pipeline/webhook-provider"),
}

TARGETENV = override_default(
    key_name="TARGETENV",
    default="sandbox",
)

PLATFORM_ENV = override_default(
    key_name="TARGETENV",
    default="root",
)
