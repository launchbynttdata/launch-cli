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


def get_token_with_secret_name(
    application_id: str,
    installation_id: str,
    signing_cert_secret_name: str,
    token_expiration_seconds: int,
) -> str:
    private_key=get_secret_value(signing_cert_secret_name)
    return get_token(
        application_id=application_id,
        installation_id=installation_id,
        private_key=private_key,
        token_expiration_seconds=token_expiration_seconds,
    )

def get_token_with_file(
    application_id: str,
    installation_id: str,
    signing_cert_file: str,
    token_expiration_seconds: int,
) -> str:
    with open(signing_cert_file, "r") as f:
        private_key = f.read()
    return get_token(
        application_id=application_id,
        installation_id=installation_id,
        private_key=private_key,
        token_expiration_seconds=token_expiration_seconds,
    )
    
def get_token(
    application_id: str,
    installation_id: str,
    private_key: str,
    token_expiration_seconds: int,
) -> str:
    try:
        signing_jwt = create_jwt(
            application_id=application_id,
            token_expiration_seconds=token_expiration_seconds,
            private_key=private_key,
        )
        headers = {"Authorization": f"Bearer {signing_jwt}"}
        response = requests.post(
            url=f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers,
        )
        return response.json()["token"]
    except ClientError as e:
        logger.exception(
            f"An error occurred while retrieving the value of token for application id {application_id}"
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
