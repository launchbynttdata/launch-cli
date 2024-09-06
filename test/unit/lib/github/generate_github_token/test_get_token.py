from unittest.mock import MagicMock, patch, mock_open

import pytest
from botocore.exceptions import ClientError

from launch.lib.github.generate_github_token import get_secret_value, get_token, get_token_with_file, get_token_with_secret_name


@pytest.fixture
def mock_dependencies():
    with patch(
        "launch.lib.github.generate_github_token.create_jwt"
    ) as mock_create_jwt, patch(
        "requests.post"
    ) as mock_post:
        mock_create_jwt.return_value = "test_jwt"
        mock_post.return_value.json.return_value = {"token": "test_token"}

        yield {
            "create_jwt": mock_create_jwt,
            "post": mock_post,
        }


def test_get_token_success(mock_dependencies):
    token = get_token(
        application_id="application_id",
        installation_id="installation_id",
        private_key="private_key", # pragma: allowlist secret
        token_expiration_seconds="token_expiration_seconds",
    )

    # Assert that the token returned is as expected
    assert (
        token == "test_token"
    ), "The token returned by get_token did not match the expected value."

    # Assert that each mock was called as expected
    mock_dependencies["create_jwt"].assert_called_once()
    mock_dependencies["post"].assert_called_once()


def test_get_token_failure(mock_dependencies):
    with pytest.raises(ClientError):
        mock_dependencies["create_jwt"].side_effect = ClientError(
            {"Error": {"Code": "TestException"}}, "test_operation"
        )
        get_token(
            application_id="application_id",
            installation_id="installation_id",
            private_key="private_key", # pragma: allowlist secret
            token_expiration_seconds="token_expiration_seconds",
        )
    mock_dependencies["post"].assert_not_called()


@pytest.fixture
def mock_secret_value():
    # Mock the Session object itself
    with patch("launch.lib.github.generate_github_token.Session") as mock_session:
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        with patch(
            "launch.lib.github.generate_github_token.Session.client"
        ) as mock_client:
            mock_client.return_value.get_secret_value.return_value = {
                "SecretString": "secret_value"  # pragma: allowlist secret
            }
            mock_session_instance.client = mock_client

            yield mock_client


def test_get_secret_value_success(mock_secret_value):
    secret_value = get_secret_value("secret_name")

    assert (
        secret_value == "secret_value"  # pragma: allowlist secret
    ), "The secret value returned by get_secret_value did not match the expected value."

    mock_secret_value.assert_called_once_with("secretsmanager")


def test_get_secret_value_exception(mock_secret_value):
    mock_secret_value.return_value.get_secret_value.side_effect = ClientError(
        {"Error": {"Code": "TestException"}}, "test_operation"
    )

    with pytest.raises(ClientError):
        get_secret_value("secret_name")

    mock_secret_value.assert_called_once_with("secretsmanager")


@pytest.fixture
def mock_private_key_dependencies():
    with patch(
        "launch.lib.github.generate_github_token.get_token"
    ) as mock_get_token, patch(
        "launch.lib.github.generate_github_token.get_secret_value"
    ) as mock_get_secret_value:
        mock_get_token.return_value = "test_token"
        mock_get_secret_value.return_value = "private_key"

        yield {
            "get_token": mock_get_token,
            "get_secret_value": mock_get_secret_value,
        }


def test_get_token_with_file_success(mocker, mock_private_key_dependencies):
    mocker.patch("builtins.open", mock_open(read_data="private_key"))

    get_token_with_file(
        application_id="application_id",
        installation_id="installation_id",
        signing_cert_file="signing_cert_file",
        token_expiration_seconds="token_expiration_seconds",
    )

    mock_private_key_dependencies["get_token"].assert_called_once_with(
        application_id="application_id",
        installation_id="installation_id",
        private_key="private_key",
        token_expiration_seconds="token_expiration_seconds",
    )


def test_get_token_with_file_failure(mocker, mock_private_key_dependencies):
    with pytest.raises(FileNotFoundError):
        mocker.patch("builtins.open", side_effect=FileNotFoundError())
        get_token_with_file(
            application_id="application_id",
            installation_id="installation_id",
            signing_cert_file="signing_cert_file",
            token_expiration_seconds="token_expiration_seconds",
        )

    mock_private_key_dependencies["get_token"].assert_not_called()


def test_get_token_with_secret_name_success(mock_private_key_dependencies):
    token = get_token_with_secret_name(
        application_id="application_id",
        installation_id="installation_id",
        signing_cert_secret_name="signing_cert_secret_name",
        token_expiration_seconds="token_expiration_seconds",
    )

    mock_private_key_dependencies["get_token"].assert_called_once_with(
        application_id="application_id",
        installation_id="installation_id",
        private_key="private_key",
        token_expiration_seconds="token_expiration_seconds",
    )


def test_get_token_with_secret_name_failure(mock_private_key_dependencies):
    with pytest.raises(ClientError):
        mock_private_key_dependencies["get_secret_value"].side_effect = ClientError(
            {"Error": {"Code": "TestException"}}, "test_operation"
        )
        get_token_with_secret_name(
            application_id="application_id",
            installation_id="installation_id",
            signing_cert_secret_name="signing_cert_secret_name",
            token_expiration_seconds="token_expiration_seconds",
        )

    mock_private_key_dependencies["get_token"].assert_not_called()
