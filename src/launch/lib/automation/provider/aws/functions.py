import json
import logging
import subprocess

logger = logging.getLogger(__name__)


def assume_role(
    aws_deployment_role: str,
    aws_deployment_region: str,
    profile: str,
) -> None:
    logger.info("Assuming the IAM deployment role")

    try:
        sts_credentials = json.loads(
            subprocess.check_output(
                [
                    "aws",
                    "sts",
                    "assume-role",
                    "--role-arn",
                    aws_deployment_role,
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
            ],
            check=True,
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.aws_secret_access_key",
                secret_access_key,
            ],
            check=True,
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.aws_session_token",
                session_token,
            ],
            check=True,
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.region",
                aws_deployment_region,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed set aws configure: {str(e)}")
