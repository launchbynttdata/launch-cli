from pathlib import Path
from unittest.mock import patch

import pytest

from launch.lib.service.common import create_specific_path


@pytest.fixture
def base_path(tmp_path) -> Path:
    return tmp_path


def test_create_specific_path_success(base_path):
    test_cases = [
        ([], [base_path]),
        (["dir"], [base_path / "dir"]),
        (["dir", "subdir"], [base_path / "dir" / "subdir"]),
    ]

    for path_parts, expected in test_cases:
        with patch.object(Path, "mkdir") as mock_mkdir:
            result = create_specific_path(base_path, path_parts)
            assert result == expected
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_create_specific_path_existing_path(base_path):
    path_parts = ["already", "exists"]
    existing_path = base_path.joinpath(*path_parts)
    existing_path.mkdir(parents=True, exist_ok=True)

    with patch.object(Path, "mkdir") as mock_mkdir:
        result = create_specific_path(base_path, path_parts)
        assert result == [existing_path]
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_create_specific_path_input_variations(base_path):
    with patch.object(Path, "mkdir") as mock_mkdir:
        create_specific_path(base_path, [])
        create_specific_path(base_path, ["one"])
        create_specific_path(base_path, ["one", "two", "three"])

        assert mock_mkdir.call_count == 3
