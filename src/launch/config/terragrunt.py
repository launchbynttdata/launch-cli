from pathlib import Path

TERRAGRUNT_RUN_DIRS = {
    "service": Path("platform/service"),
    "pipeline": Path("platform/pipeline/pipeline"),
    "webhook": Path("platform/pipeline/webhooks"),
}
