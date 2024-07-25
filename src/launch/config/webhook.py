from launch.env import override_default

WEBHOOK_GIT_REPO_URL = override_default(
    key_name="WEBHOOK_GIT_REPO_URL",
    default="https://github.com/launchbynttdata/git-webhook-lambda.git",
)

WEBHOOK_GIT_REPO_TAG = override_default(
    key_name="WEBHOOK_GIT_REPO_TAG",
    default="main",
)

WEBHOOK_BUILD_SCRIPT = override_default(
    key_name="WEBHOOK_BUILD_SCRIPT",
    default="build_deployable_zip.sh",
)

WEBHOOK_ZIP = override_default(
    key_name="WEBHOOK_ZIP",
    default="lambda.zip",
)
