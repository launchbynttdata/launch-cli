from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from launch.lib.service.template.functions import expand_wildcards


@pytest.fixture
def current_path(tmp_path) -> Path:
    return tmp_path


def test_expand_wildcards_empty_remaining_parts(current_path):
    result = expand_wildcards(current_path, [])
    assert result == [current_path]


def test_expand_wildcards_single_wildcard(current_path):
    subdir1 = current_path / "subdir1"
    subdir1.mkdir()

    subdir2 = current_path / "subdir2"
    subdir2.mkdir()

    list_directories_mock = MagicMock(return_value=[subdir1, subdir2])

    with patch(
        "launch.lib.service.template.functions.list_directories", list_directories_mock
    ):
        result = expand_wildcards(current_path, ["*"])
        assert result == [subdir1, subdir2]


def test_expand_wildcards_specific_directory(current_path):
    next_part = "subdir1"
    next_path = current_path / next_part
    next_path.mkdir()

    result = expand_wildcards(current_path, [next_part])
    assert result == [next_path]


def test_expand_wildcards_multiple_wildcards(current_path):
    subdir1 = current_path / "subdir1"
    subdir1.mkdir()
    subdir2 = subdir1 / "subdir2"
    subdir2.mkdir()
    subdir3 = subdir2 / "subdir3"
    subdir3.mkdir()

    list_directories_mock = MagicMock(return_value=[subdir1])

    with MagicMock() as list_directories_mock:
        list_directories_mock.return_value = [subdir1]
        result = expand_wildcards(current_path, ["*", "*", "*"])

    assert result == [subdir3]
