from launch.env import override_default

TERRAFORM_VAR_FILE = override_default(
    key_name="TERRAFORM_VAR_FILE",
    default="terraform.tfvars",
)
