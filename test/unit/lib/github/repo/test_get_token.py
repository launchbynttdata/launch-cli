# from unittest.mock import MagicMock, patch

# import pytest
# from boto3.session import Session
# from botocore.exceptions import ClientError

# from launch.lib.github.generate_github_token import (
#     get_secret_value,
#     get_ssm_parameter,
#     get_token,
# )


# @pytest.fixture
# def mock_dependencies():
#     with patch(
#         "launch.lib.github.generate_github_token.get_ssm_parameter"
#     ) as mock_get_ssm_parameter, patch(
#         "launch.lib.github.generate_github_token.create_jwt"
#     ) as mock_create_jwt, patch(
#         "launch.lib.github.generate_github_token.get_secret_value"
#     ) as mock_get_secret_value, patch(
#         "requests.post"
#     ) as mock_post:
#         # Setup mock return values
#         mock_get_ssm_parameter.side_effect = (
#             lambda x, *args, **kwargs: x + "_value"
#         )  # Simulate returning a value based on parameter name
#         mock_create_jwt.return_value = "test_jwt"
#         mock_get_secret_value.return_value = "private_key"
#         mock_post.return_value.json.return_value = {"token": "test_token"}

#         yield {
#             "get_ssm_parameter": mock_get_ssm_parameter,
#             "create_jwt": mock_create_jwt,
#             "get_secret_value": mock_get_secret_value,
#             "post": mock_post,
#         }


# def test_get_token_success(mock_dependencies):
#     token = get_token(
#         "application_id",
#         "installation_id",
#         "signing_cert_secret",
#         "token_expiration_seconds",
#         "aws_profile",
#     )

#     # Assert that the token returned is as expected
#     assert (
#         token == "test_token"
#     ), "The token returned by get_token did not match the expected value."

#     # Assert that each mock was called as expected
#     mock_dependencies["get_ssm_parameter"].assert_any_call(
#         "application_id", "aws_profile", False
#     )
#     mock_dependencies["get_ssm_parameter"].assert_any_call(
#         "installation_id", "aws_profile", False
#     )
#     mock_dependencies["get_ssm_parameter"].assert_any_call(
#         "signing_cert_secret", "aws_profile", False
#     )
#     mock_dependencies["create_jwt"].assert_called_once()
#     mock_dependencies["post"].assert_called_once()


# def test_get_token_failure(mock_dependencies):
#     mock_dependencies["get_ssm_parameter"].side_effect = ClientError(
#         error_response={"Error": {"Code": "ParameterNotFound"}},
#         operation_name="get_parameter",
#     )

#     with pytest.raises(ClientError):
#         get_token(
#             "application_id",
#             "installation_id",
#             "signing_cert_secret",
#             "token_expiration_seconds",
#             "aws_profile",
#         )

#     mock_dependencies["get_ssm_parameter"].assert_any_call(
#         "application_id", "aws_profile", False
#     )
#     mock_dependencies["create_jwt"].assert_not_called()
#     mock_dependencies["post"].assert_not_called()


# @pytest.fixture
# def mock_ssm_parameter():
#     # Mock the Session object itself
#     with patch("launch.lib.github.generate_github_token.Session") as mock_session:
#         mock_session_instance = MagicMock()
#         mock_session.return_value = mock_session_instance

#         with patch(
#             "launch.lib.github.generate_github_token.Session.client"
#         ) as mock_client:
#             mock_client.return_value.get_parameter.return_value = {
#                 "Parameter": {"Value": "test_value"}
#             }
#             mock_session_instance.client = mock_client

#             yield mock_client


# def test_get_ssm_parameter_success(mock_ssm_parameter):
#     parameter_value = get_ssm_parameter("parameter_name", "aws_profile", False)

#     assert (
#         parameter_value == "test_value"
#     ), "The parameter value returned by get_ssm_parameter did not match the expected value."

#     mock_ssm_parameter.assert_called_once_with("ssm")


# def test_get_ssm_parameter_exception(mock_ssm_parameter):
#     mock_ssm_parameter.return_value.get_parameter.side_effect = ClientError(
#         {"Error": {"Code": "TestException"}}, "test_operation"
#     )

#     with pytest.raises(ClientError):
#         get_ssm_parameter("parameter_name", "aws-profile", False)

#     mock_ssm_parameter.assert_called_once_with("ssm")


# @pytest.fixture
# def mock_secret_value():
#     # Mock the Session object itself
#     with patch("launch.lib.github.generate_github_token.Session") as mock_session:
#         mock_session_instance = MagicMock()
#         mock_session.return_value = mock_session_instance

#         with patch(
#             "launch.lib.github.generate_github_token.Session.client"
#         ) as mock_client:
#             mock_client.return_value.get_secret_value.return_value = {
#                 "SecretString": "secret_value"  # pragma: allowlist secret
#             }
#             mock_session_instance.client = mock_client

#             yield mock_client


# def test_get_secret_value_success(mock_secret_value):
#     secret_value = get_secret_value("secret_name", "aws_profile")

#     assert (
#         secret_value == "secret_value"  # pragma: allowlist secret
#     ), "The secret value returned by get_secret_value did not match the expected value."

#     mock_secret_value.assert_called_once_with("secretsmanager")


# def test_get_secret_value_exception(mock_secret_value):
#     mock_secret_value.return_value.get_secret_value.side_effect = ClientError(
#         {"Error": {"Code": "TestException"}}, "test_operation"
#     )

#     with pytest.raises(ClientError):
#         get_secret_value("secret_name", "aws_profile")

#     mock_secret_value.assert_called_once_with("secretsmanager")
