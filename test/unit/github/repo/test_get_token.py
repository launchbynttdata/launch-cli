from unittest.mock import MagicMock, patch

import pytest

from launch.github.generate_github_token import get_token


@pytest.fixture
def mock_dependencies():
    with patch(
        "launch.github.generate_github_token.get_ssm_parameter"
    ) as mock_get_ssm_parameter, patch(
        "launch.github.generate_github_token.create_jwt"
    ) as mock_create_jwt, patch(
        "launch.github.generate_github_token.get_secret_value"
    ) as mock_get_secret_value, patch(
        "requests.post"
    ) as mock_post:
        # Setup mock return values
        mock_get_ssm_parameter.side_effect = (
            lambda x: x + "_value"
        )  # Simulate returning a value based on parameter name
        mock_create_jwt.return_value = "test_jwt"
        mock_get_secret_value.return_value = "private_key"
        mock_post.return_value.json.return_value = {"token": "test_token"}

        yield {
            "get_ssm_parameter": mock_get_ssm_parameter,
            "create_jwt": mock_create_jwt,
            "get_secret_value": mock_get_secret_value,
            "post": mock_post,
        }


def test_get_token_success(mock_dependencies):
    token = get_token("application_id", "installation_id", "signing_cert_secret")

    # Assert that the token returned is as expected
    assert (
        token == "test_token"
    ), "The token returned by get_token did not match the expected value."

    # Assert that each mock was called as expected
    mock_dependencies["get_ssm_parameter"].assert_any_call("application_id")
    mock_dependencies["get_ssm_parameter"].assert_any_call("installation_id")
    mock_dependencies["get_ssm_parameter"].assert_any_call("signing_cert_secret")
    mock_dependencies["create_jwt"].assert_called_once()
    mock_dependencies["post"].assert_called_once()


# Additional tests can be written to cover error handling, different return values, etc.
