from launch.env import override_default

AZDO_ORG_SERVICE_URL = override_default(
    key_name="AZDO_ORG_SERVICE_URL",
    default="https://dev.azure.com/launch-dso",
)