import json
import logging
import subprocess

from launch.lib.automation.common.functions import read_key_value_from_file

logger = logging.getLogger(__name__)


def assume_role(
    provider_config: dict, repository_name: str, target_environment: str
) -> None:
    logger.info("Assuming the IAM deployment role")

    provider = provider_config["provider"]
    profile = provider_config[provider]["role_arn"]

    try:
        sts_credentials = json.loads(
            subprocess.check_output(
                [
                    "aws",
                    "sts",
                    "assume-role",
                    "--role-arn",
                    provider_config[provider]["role_arn"],
                    "--role-session-name",
                    "caf-build-agent",
                ]
            )
        )
    except Exception as e:
        raise RuntimeError(f"Failed aws sts assume-role: {str(e)}") from e

    access_key = sts_credentials["Credentials"]["AccessKeyId"]
    secret_access_key = sts_credentials["Credentials"]["SecretAccessKey"]
    session_token = sts_credentials["Credentials"]["SessionToken"]

    try:
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.aws_access_key_id",
                access_key,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.aws_secret_access_key",
                secret_access_key,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.aws_session_token",
                session_token,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.region",
                provider_config[provider]["region"],
            ]
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed set aws configure: {str(e)}")
