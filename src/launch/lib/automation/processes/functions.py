import logging
import subprocess

logger = logging.getLogger(__name__)


def make_configure() -> None:
    logger.info(f"Running make configure")
    try:
        subprocess.run(["make", "configure"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
