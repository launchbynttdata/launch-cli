from semver import Version

VERSION = "0.6.0"

SEMANTIC_VERSION = Version.parse(VERSION)
GITHUB_ORG_NAME = "launchbynttdata"
GITHUB_REPO_NAME = "launch-cli"
SERVICE_SKELETON = "https://github.com/launchbynttdata/lcaf-skeleton-terragrunt.git"
SKELETON_BRANCH = "main"
MAIN_BRANCH = "main"
INIT_BRANCH = "feature/init"
BUILD_DEPENDENCIES_DIR = ".launch"
CODE_GENERATION_DIR_SUFFIX = "-singleRun"
DISCOVERY_FORBIDDEN_DIRECTORIES = [
    ".git",
    "components",
    ".repo",
    "__pycache__",
    ".venv",
    ".terraform",
    ".terragrunt-cache",
]
