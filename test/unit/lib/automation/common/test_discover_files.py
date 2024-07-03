import pathlib
from typing import Generator

import pytest

from launch.lib.automation.common.functions import discover_files


@pytest.fixture
def example_structure(tmp_path) -> Generator[pathlib.Path, None, None]:
    tmp_path.joinpath("dir_one").mkdir(parents=True)
    tmp_path.joinpath("dir_one/file_one.txt").write_text("foo")
    tmp_path.joinpath("dir_two").mkdir(parents=True)
    tmp_path.joinpath("dir_two/file_two.jpg").write_bytes(b"bar")
    tmp_path.joinpath("dir_three").mkdir(parents=True)
    tmp_path.joinpath("dir_three/file_three.txt").write_text("baz")
    tmp_path.joinpath(".git/usually_forbidden").mkdir(parents=True)
    tmp_path.joinpath(".git/usually_forbidden/forbidden_file.txt").write_text("foo")
    yield tmp_path


def test_discover_all(example_structure):
    expected_files = [
        example_structure.joinpath("dir_one/file_one.txt"),
        example_structure.joinpath("dir_two/file_two.jpg"),
        example_structure.joinpath("dir_three/file_three.txt"),
    ]

    discovered = discover_files(root_path=example_structure)
    assert all(expected in discovered for expected in expected_files)


def test_discover_partial_name_match(example_structure):
    expected_files = [
        example_structure.joinpath("dir_one/file_one.txt"),
        example_structure.joinpath("dir_three/file_three.txt"),
    ]

    discovered = discover_files(root_path=example_structure, filename_partial="txt")
    assert all(expected in discovered for expected in expected_files)


def test_discover_replace_forbidden(example_structure):
    expected_files = [
        example_structure.joinpath("dir_one/file_one.txt"),
        example_structure.joinpath("dir_three/file_three.txt"),
        example_structure.joinpath(".git/usually_forbidden/forbidden_file.txt"),
    ]
    forbidden = "dir_two"

    discovered = discover_files(
        root_path=example_structure, forbidden_directories=[forbidden]
    )
    assert all(expected in discovered for expected in expected_files)
