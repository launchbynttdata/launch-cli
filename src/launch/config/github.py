from launch.env import override_default

GITHUB_ORG_NAME = override_default(
    key_name="GITHUB_ORG_NAME", default="launchbynttdata"
)
GITHUB_REPO_NAME = override_default(key_name="GITHUB_REPO_NAME", default="launch-cli")
GITHUB_ORG_PLATFORM_TEAM = override_default(
    key_name="GITHUB_ORG_PLATFORM_TEAM", default="platform-team"
)
GITHUB_ORG_PLATFORM_TEAM_ADMINISTRATORS = override_default(
    key_name="GITHUB_ORG_PLATFORM_TEAM_ADMINISTRATORS",
    default="platform-administrators",
)

GIT_SCM_ENDPOINT = override_default(key_name="GIT_SCM_ENDPOINT", default="github.com")

GIT_MACHINE_USER = override_default(
    key_name="GIT_MACHINE_USER", default="launch-cli-user"
)
