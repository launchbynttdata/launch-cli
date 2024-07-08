import json
from pathlib import Path

import pytest

from launch.lib.automation.common.functions import traverse_with_callback


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


def test_traverse_with_callback_simple_dict(mocker, fakedata):
    mock_callback = mocker.Mock(return_value=None)
    initial_path = Path("platform")

    traverse_with_callback(
        fakedata["simple_dict"], mock_callback, current_path=initial_path
    )

    assert mock_callback.call_count == 2
    mock_callback.assert_any_call(
        key="key1",
        value="value1",
        dictionary=fakedata["simple_dict"],
        current_path=initial_path,
        nested_dict=fakedata["simple_dict"],
    )
    mock_callback.assert_any_call(
        key="key2",
        value="value2",
        dictionary=fakedata["simple_dict"],
        current_path=initial_path,
        nested_dict=fakedata["simple_dict"],
    )


def test_traverse_with_callback_nested_dict(mocker, fakedata):
    mock_callback = mocker.Mock(return_value=None)
    nested_dict = fakedata["nested_dict"]
    initial_path = Path("platform")

    traverse_with_callback(nested_dict, mock_callback, current_path=initial_path)

    assert mock_callback.call_count == 4
    mock_callback.assert_any_call(
        key="key2_1",
        value="value2_1",
        dictionary=nested_dict["key2"],
        current_path=initial_path / "key2",
        nested_dict=nested_dict["key2"],
    )
