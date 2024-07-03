import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from launch.lib.automation.common.functions import load_yaml
from launch.lib.service.common import write_text


def test_write_text_json(fakedata):
    serialized_data = json.dumps(fakedata["copy_and_render"]["context_data"], indent=4)
    test_path = MagicMock(spec=Path)
    test_path.write_text.return_value = MagicMock()
    write_text(
        path=test_path,
        data=fakedata["copy_and_render"]["context_data"],
        output_format="json",
    )
    test_path.write_text.assert_called_once_with(serialized_data)


def test_write_text_yaml(fakedata, tmp_path):
    serialized_data = fakedata["copy_and_render"]["context_data"]
    target_path = tmp_path.joinpath("sample.yaml")
    write_text(
        path=target_path,
        data=serialized_data,
        output_format="yaml",
    )
    deserialized = load_yaml(yaml_file=target_path)
    assert deserialized == serialized_data


def test_write_text_unsupported_format(fakedata):
    unsupported_format = "xml"
    test_path = MagicMock(spec=Path)
    test_path.write_text.return_value = MagicMock()

    with patch("launch.lib.service.common.logger.error") as mock_log_error:
        with pytest.raises(ValueError) as exc_info:
            write_text(
                path=test_path,
                data=fakedata["copy_and_render"]["context_data"],
                output_format=unsupported_format,
            )

    test_path.write_text.assert_not_called()
    mock_log_error.assert_called_once_with(
        f"Unsupported output format: {unsupported_format}"
    )
    assert (
        str(exc_info.value) == f"Unsupported output format: {unsupported_format}"
    ), "A ValueError with the correct message should be raised for unsupported formats"
