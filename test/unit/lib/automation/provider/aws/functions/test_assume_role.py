import unittest
from unittest.mock import patch
import subprocess
import json

from launch.lib.automation.provider.aws.functions import assume_role

class TestAssumeRole(unittest.TestCase):

    def aws_setup(self):
        aws_deployment_role = "arn:aws:iam::123456789012:role/test-role"
        aws_deployment_region = "us-west-2"
        profile = "test-profile"
        sts_response = {
                "Credentials": {
                    "AccessKeyId": "test-access-key-id",
                    "SecretAccessKey": "test-secret-access-key",
                    "SessionToken": "test-session-token"
                }
         }
        return aws_deployment_role, aws_deployment_region, profile,sts_response

    def test_assume_role_success(self):
        with patch("subprocess.check_output") as mock_check_output, patch("subprocess.run") as mock_run:
            aws_deployment_role, aws_deployment_region, profile, sts_response = self.aws_setup()
            mock_check_output.return_value = json.dumps(sts_response).encode('utf-8')
            
            assume_role(aws_deployment_role, aws_deployment_region, profile)
            
            mock_check_output.assert_called_once_with([
                "aws",
                "sts",
                "assume-role",
                "--role-arn",
                aws_deployment_role,
                "--role-session-name",
                "caf-build-agent",
            ])

            mock_run.assert_called_with(
            [
                "aws",
                "configure",
                "set",
                f"profile.{profile}.region",
                "us-west-2",
            ],
            check=True,
            )   

    def test_assume_role_assume_role_failure(self):
        with patch("subprocess.check_output") as mock_check_output:
            aws_deployment_role, aws_deployment_region, profile,_ = self.aws_setup()
            mock_check_output.side_effect = subprocess.CalledProcessError(1, "aws sts assume-role")
            
            with self.assertRaises(RuntimeError) as context:
                assume_role(aws_deployment_role, aws_deployment_region, profile)
            
            self.assertIn("Failed aws sts assume-role", str(context.exception))

    def test_assume_role_configure_failure(self):
        with patch("subprocess.check_output") as mock_check_output, patch("subprocess.run") as mock_run:
            aws_deployment_role, aws_deployment_region, profile, sts_response = self.aws_setup()
            mock_check_output.return_value = json.dumps(sts_response).encode('utf-8')
            mock_run.side_effect = subprocess.CalledProcessError(1, "aws configure set")
            
            with self.assertRaises(RuntimeError) as context:
                assume_role(aws_deployment_role, aws_deployment_region, profile)
            
            self.assertIn("Failed set aws configure", str(context.exception))
