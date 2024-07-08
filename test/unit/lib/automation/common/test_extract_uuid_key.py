from launch.lib.automation.common.functions import extract_uuid_key


def test_uuid_extract_maintains_structure():
    input = {
        "platform": {
            "service": {
                "sandbox": {
                    "eastus": {
                        "000": {
                            "properties_file": ".launch/platform/service/sandbox/eastus/000/terraform.tfvars",
                            "uuid": "14a8f6",
                        }
                    }
                }
            }
        }
    }

    output = extract_uuid_key(source_data=input)

    assert output == {
        "platform": {"service": {"sandbox": {"eastus": {"000": {"uuid": "14a8f6"}}}}}
    }


def test_uuid_extract_not_found():
    input = {
        "platform": {
            "service": {
                "sandbox": {
                    "eastus": {
                        "000": {
                            "properties_file": ".launch/platform/service/sandbox/eastus/000/terraform.tfvars"
                        }
                    }
                }
            }
        }
    }

    output = extract_uuid_key(source_data=input)

    assert output == {"platform": {"service": {"sandbox": {"eastus": {"000": {}}}}}}
