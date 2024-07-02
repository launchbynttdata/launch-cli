import sys
import time
from pathlib import Path

import boto3
import requests
from botocore.exceptions import ClientError
from jwt import PyJWT


def create_jwt(
    application_id: int, private_key: bytes, expiration_seconds: int = 600
) -> str:
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + expiration_seconds,
        "iss": application_id,
    }
    jwt_instance = PyJWT()
    encoded_jwt = jwt_instance.encode(
        payload=payload, key=private_key, algorithm="RS256"
    )
    return encoded_jwt


def get_token(
    application_id_parameter_name: str,
    installation_id_parameter_name: str,
    signing_cert_secret_name: str,
) -> str:
    application_id = get_ssm_parameter(application_id_parameter_name)
    installation_id = get_ssm_parameter(installation_id_parameter_name)
    signing_cert_secret_cm_name = get_ssm_parameter(signing_cert_secret_name)

    signing_jwt = create_jwt(
        application_id=application_id,
        private_key=get_secret_value(signing_cert_secret_cm_name),
    )
    headers = {"Authorization": f"Bearer {signing_jwt}"}
    response = requests.post(
        url=f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
    )
    return response.json()["token"]


def get_ssm_parameter(parameter_name):
    """
    Retrieves the value of an SSM parameter by its name.

    Parameters:
    - parameter_name (str): The name of the SSM parameter.

    Returns:
    - str: The value of the SSM parameter.
    """
    # Create a session using AWS SDK
    ssm = boto3.client("ssm")

    try:
        # Get the parameter
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        # Extract the parameter value
        parameter_value = response["Parameter"]["Value"]
        return parameter_value
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


def get_secret_value(secret_name):
    """
    Retrieves the value of a secret from AWS Secrets Manager by its name.

    Parameters:
    - secret_name (str): The name of the secret.

    Returns:
    - str: The value of the secret.
    """
    # Create a session using AWS SDK
    client = boto3.client("secretsmanager")

    try:
        # Get the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Secrets Manager stores the secret as a string or binary, so check the type
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            # For binary secret data, we assume it's encoded in base64 and decode it to a string
            secret = base64.b64decode(get_secret_value_response["SecretBinary"]).decode(
                "utf-8"
            )

        return secret
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
