import logging
import time

import requests
from boto3.session import Session
from botocore.exceptions import ClientError
from jwt import PyJWT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_jwt(
    application_id: int, token_expiration_seconds: int, private_key: bytes
) -> str:
    current_time_in_epoch_seconds = time.time()
    expiration_time_in_epoch_seconds = (
        current_time_in_epoch_seconds + token_expiration_seconds
    )
    payload = {
        "iat": int(current_time_in_epoch_seconds),
        "exp": int(expiration_time_in_epoch_seconds),
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
    token_expiration_seconds: int,
) -> str:
    try:
        application_id = get_ssm_parameter(application_id_parameter_name, False)
        installation_id = get_ssm_parameter(installation_id_parameter_name, False)
        signing_cert_secret_cm_name = get_ssm_parameter(signing_cert_secret_name, False)

        signing_jwt = create_jwt(
            application_id=application_id,
            token_expiration_seconds=token_expiration_seconds,
            private_key=get_secret_value(signing_cert_secret_cm_name),
        )
        headers = {"Authorization": f"Bearer {signing_jwt}"}
        response = requests.post(
            url=f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers,
        )
        return response.json()["token"]
    except ClientError as e:
        logger.exception(
            f"An error occurred while retrieving the value of token for application id {application_id_parameter_name}"
        )
        raise e


def get_ssm_parameter(parameter_name: str, with_decryption: bool = True) -> str:
    """
    Retrieves the value of an SSM parameter by its name.

    Parameters:
    - parameter_name (str): The name of the SSM parameter.
    - with_decryption (bool): Whether to decrypt the parameter value.

    Returns:
    - str: The value of the SSM parameter.
    """
    # Create a session with the specified AWS profile
    session = Session()

    # Create a session using AWS SDK
    ssm = session.client("ssm")

    try:
        # Get the parameter
        response = ssm.get_parameter(
            Name=parameter_name, WithDecryption=with_decryption
        )
        # Extract the parameter value
        parameter_value = response["Parameter"]["Value"]
        return parameter_value
    except ClientError as e:
        logger.exception(
            f"An error occurred while retrieving the value of {parameter_name}"
        )
        raise e


def get_secret_value(secret_name: str) -> str:
    """
    Retrieves the value of a secret from AWS Secrets Manager by its name.

    Parameters:
    - secret_name (str): The name of the secret.

    Returns:
    - str: The value of the secret.
    """
    # Create a session with the specified AWS profile
    session = Session()

    # Create a session using AWS SDK
    secretsmanager = session.client("secretsmanager")

    try:
        # Get the secret value
        get_secret_value_response = secretsmanager.get_secret_value(
            SecretId=secret_name
        )

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
        logger.exception(
            f"An error occurred while retrieving the value of {secret_name}"
        )
        raise e
