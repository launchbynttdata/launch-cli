import json
import logging
import subprocess

logger = logging.getLogger(__name__)


def assume_role(
    aws_deployment_role: str,
    aws_deployment_region: str,
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
                f"profile.{aws_deployment_role}.aws_access_key_id",
                access_key,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{aws_deployment_role}.aws_secret_access_key",
                secret_access_key,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{aws_deployment_role}.aws_session_token",
                session_token,
            ]
        )
        subprocess.run(
            [
                "aws",
                "configure",
                "set",
                f"profile.{aws_deployment_role}.region",
                aws_deployment_region,
            ]
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed set aws configure: {str(e)}")
