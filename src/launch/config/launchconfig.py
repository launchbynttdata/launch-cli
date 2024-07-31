from launch.env import override_default

SERVICE_MAIN_BRANCH = override_default(
    key_name="SERVICE_MAIN_BRANCH",
    default="main",
)

SERVICE_REMOTE_BRANCH = override_default(
    key_name="SERVICE_REMOTE_BRANCH",
    default="feature/init",
)

SERVICE_SKELETON = override_default(
    key_name="SERVICE_SKELETON",
    default="https://github.com/launchbynttdata/lcaf-template-terragrunt.git",
)

SKELETON_BRANCH = override_default(
    key_name="SKELETON_BRANCH",
    default="main",
)
