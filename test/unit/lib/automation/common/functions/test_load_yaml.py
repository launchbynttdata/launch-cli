import pathlib

from launch.lib.automation.common.functions import load_yaml


def test_load_yaml_simple():
    simple_yaml_path = pathlib.Path(__file__).parent.joinpath("data/simple.yaml")
    yaml_result = load_yaml(yaml_file=simple_yaml_path)
    expected_list_values = ["list", "value"]
    expected_map_value = {"nested_key": "nested_value"}

    assert yaml_result["simple_key"] == "string value"
    assert isinstance(yaml_result["list_key"], list)
    assert len(yaml_result["list_key"]) == 2
    assert all(
        expected_value in yaml_result["list_key"]
        for expected_value in expected_list_values
    )
    assert isinstance(yaml_result["map_key"], dict)
    assert all(
        item in yaml_result["map_key"].items() for item in expected_map_value.items()
    )
