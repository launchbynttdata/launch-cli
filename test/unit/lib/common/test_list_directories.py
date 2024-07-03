from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.lib.service.common import list_directories


@pytest.fixture
def directory(tmp_path) -> Path:
    return tmp_path


def test_list_directories_no_subdirectories(directory):
    subdirs = list_directories(directory)
    assert subdirs == []


def test_list_directories_with_subdirectories(directory):
    subdir1 = directory / "subdir1"
    subdir1.mkdir()

    subdir2 = directory / "subdir2"
    subdir2.mkdir()

    subdirs = list_directories(directory)
    assert subdir1 in subdirs
    assert subdir2 in subdirs


def test_list_directories_nonexistent_directory():
    nonexistent_directory = Path("nonexistent_directory")
    with pytest.raises(FileNotFoundError):
        list_directories(nonexistent_directory)


def test_list_directories_permission_error(tmp_path):
    directory = tmp_path / "protected_directory"
    directory.mkdir()
    # Make directory inaccessible
    directory.chmod(0o000)

    with pytest.raises(PermissionError):
        list_directories(directory)

    # Reset permissions
    directory.chmod(0o777)


def test_list_directories_mock(tmp_path):
    directory = tmp_path / "mock_directory"
    directory.mkdir()

    subdirs = [directory / f"subdir{i}" for i in range(3)]
    mock_iterdir = MagicMock(return_value=subdirs)

    with MagicMock() as mock_iterdir:
        subdirs = list_directories(directory)

    assert subdirs == subdirs
