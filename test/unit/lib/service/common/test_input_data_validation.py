from launch.config.launchconfig import SERVICE_SKELETON, SKELETON_BRANCH
from launch.lib.service.common import input_data_validation


def test_input_data_validation_missing_skeleton():
    input_data = {}
    expected_output = {
        "skeleton": {
            "url": SERVICE_SKELETON,
            "tag": SKELETON_BRANCH,
        }
    }

    result = input_data_validation(input_data)
    assert result == expected_output


def test_input_data_validation_missing_url_and_tag():
    input_data = {"skeleton": {}}
    expected_output = {
        "skeleton": {
            "url": SERVICE_SKELETON,
            "tag": SKELETON_BRANCH,
        }
    }

    result = input_data_validation(input_data)
    assert result == expected_output


def test_input_data_validation_with_all_data_provided():
    input_data = {
        "skeleton": {
            "url": "custom_url",
            "tag": "custom_tag",
        }
    }
    expected_output = input_data.copy()

    result = input_data_validation(input_data)
    assert result == expected_output
