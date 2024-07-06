import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def install_tool_versions(file: str) -> None:
    logger.info("Installing all asdf plugins under .tool-versions")
    try:
        with open(file, "r") as file:
            lines = file.readlines()

        for line in lines:
            plugin = line.split()[0]
            subprocess.run(["asdf", "plugin", "add", plugin])

        subprocess.run(["asdf", "install"])
    except Exception as e:
        raise RuntimeError(
            f"An error occurred with asdf install {file}: {str(e)}"
        ) from e


def set_netrc(password: str, machine: str, login: str) -> None:
    logger.info("Setting ~/.netrc variables")
    try:
        with open(os.path.expanduser("~/.netrc"), "a") as file:
            file.write(f"machine {machine}\n")
            file.write(f"login {login}\n")
            file.write(f"password {password}\n")

        os.chmod(os.path.expanduser("~/.netrc"), 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
