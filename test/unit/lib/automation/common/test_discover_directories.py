import pathlib
from typing import Generator

import pytest

from launch.lib.automation.common.functions import discover_directories


@pytest.fixture
def example_directories(tmp_path) -> Generator[pathlib.Path, None, None]:
    tmp_path.joinpath("deeply/nested/directory").mkdir(parents=True)
    tmp_path.joinpath("deeply/.git/usually_forbidden").mkdir(parents=True)
    yield tmp_path


def test_discover_all(example_directories):
    expected_directories = [
        example_directories.joinpath("deeply"),
        example_directories.joinpath("deeply/nested"),
        example_directories.joinpath("deeply/nested/directory"),
    ]

    discovered = discover_directories(root_path=example_directories)
    assert all(expected in discovered for expected in expected_directories)


def test_discover_partial_name_match(example_directories):
    expected_directories = [example_directories.joinpath("deeply")]

    discovered = discover_directories(
        root_path=example_directories, dirname_partial="ly"
    )
    assert all(expected in discovered for expected in expected_directories)


def test_discover_replace_forbidden(example_directories):
    expected_directories = [
        example_directories.joinpath("deeply"),
        example_directories.joinpath("deeply/nested"),
        example_directories.joinpath("deeply/.git"),
        example_directories.joinpath("deeply/.git/usually_forbidden"),
    ]
    forbidden = "directory"

    discovered = discover_directories(
        root_path=example_directories, forbidden_directories=[forbidden]
    )
    assert all(expected in discovered for expected in expected_directories)
