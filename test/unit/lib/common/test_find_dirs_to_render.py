from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.lib.service.common import find_dirs_to_render


def test_find_dirs_to_render_no_wildcards(base_path):
    path_parts = ["dir1", "dir2"]
    expected_result = [Path(base_path) / "dir1" / "dir2"]
    result = find_dirs_to_render(base_path, path_parts)
    assert result == expected_result


def test_find_dirs_to_render_with_wildcards(base_path):
    path_parts = ["*", "dir2"]
    subdir1 = Path(base_path) / "subdir1"
    subdir1.mkdir()

    subdir2 = subdir1 / "dir2"
    subdir2.mkdir()

    with MagicMock() as expand_wildcards_mock:
        expand_wildcards_mock.return_value = [subdir2]
        result = find_dirs_to_render(base_path, path_parts)

    assert result == [subdir2]


def test_find_dirs_to_render_no_matching_directories(base_path):
    path_parts = ["nonexistent_dir", "*"]
    result = find_dirs_to_render(base_path, path_parts)
    assert result == []


def test_find_dirs_to_render_permission_error(tmp_path):
    base_path = tmp_path / "protected_base_path"
    base_path.mkdir()
    # Make base path inaccessible
    base_path.chmod(0o000)

    path_parts = ["dir"]
    with pytest.raises(PermissionError):
        find_dirs_to_render(str(base_path), path_parts)

    # Reset permissions
    base_path.chmod(0o777)


def test_find_dirs_to_render_mock(tmp_path):
    base_path = tmp_path / "mock_base_path"
    base_path.mkdir()

    path_parts = ["*"]
    subdir = base_path / "subdir"
    subdir.mkdir()

    with MagicMock() as expand_wildcards_mock:
        expand_wildcards_mock.return_value = [subdir]
        result = find_dirs_to_render(str(base_path), path_parts)

    assert result == [subdir]
