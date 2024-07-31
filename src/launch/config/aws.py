from launch.env import override_default

AWS_REGION = override_default(
    key_name="AWS_REGION",
    default="us-east-2",
)

AWS_DEPLOYMENT_ROLE = override_default(
    key_name="AWS_DEPLOYMENT_ROLE",
    default=None,
)

AWS_DEPLOYMENT_REGION = override_default(
    key_name="AWS_DEPLOYMENT_REGION",
    default=AWS_REGION,
)

AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE = override_default(
    key_name="AWS_LAMBDA_CODEBUILD_ENV_VAR_FILE",
    default="set_vars.sh",
)

SM_AWS_PROFILE = override_default(
    key_name="SM_AWS_PROFILE",
    default="default",
)

SM_AWS_REGION = override_default(
    key_name="SM_AWS_REGION",
    default=AWS_REGION,
)
