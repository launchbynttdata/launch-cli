import pathlib
import shutil
from typing import Generator

import pytest

from launch.lib.automation.common.functions import unpack_archive


@pytest.fixture
def isolated_tgz_path(tmp_path) -> Generator[pathlib.Path, None, None]:
    simple_tgz_path = pathlib.Path(__file__).parent.joinpath("data/simple.tgz")
    isolated_tgz_file = tmp_path.joinpath(simple_tgz_path.name)
    shutil.copy(src=simple_tgz_path, dst=isolated_tgz_file)
    yield isolated_tgz_file.parent


class TestUnpackArchiveTgz:
    def test_unpack_archive_simple_tgz_existing_destination(self, isolated_tgz_path):
        expected_unpacked_directory: pathlib.Path = isolated_tgz_path.joinpath(
            "nested_directory"
        )
        expected_unpacked_file = expected_unpacked_directory.joinpath("hello.txt")
        expected_unpacked_file_contents = "hello world"

        unpack_archive(
            archive_path=isolated_tgz_path.joinpath("simple.tgz"),
            destination=isolated_tgz_path,
        )

        assert (
            expected_unpacked_directory.exists()
            and expected_unpacked_directory.is_dir()
        )
        assert expected_unpacked_file.exists() and expected_unpacked_file.is_file()
        assert expected_unpacked_file_contents in expected_unpacked_file.read_text()

    def test_unpack_archive_simple_tgz_create_destination(self, isolated_tgz_path):
        deeper_directory = isolated_tgz_path.joinpath("deeper/nested/path")

        expected_unpacked_directory: pathlib.Path = deeper_directory.joinpath(
            "nested_directory"
        )
        expected_unpacked_file = expected_unpacked_directory.joinpath("hello.txt")
        expected_unpacked_file_contents = "hello world"

        unpack_archive(
            archive_path=isolated_tgz_path.joinpath("simple.tgz"),
            destination=deeper_directory,
        )

        assert (
            expected_unpacked_directory.exists()
            and expected_unpacked_directory.is_dir()
        )
        assert expected_unpacked_file.exists() and expected_unpacked_file.is_file()
        assert expected_unpacked_file_contents in expected_unpacked_file.read_text()

    def test_archive_not_exists(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            unpack_archive(archive_path=tmp_path.joinpath("not_exists.tgz"))

    def test_destination_exists_not_directory(self, isolated_tgz_path):
        not_a_dir: pathlib.Path = isolated_tgz_path.joinpath("not_a_dir")
        not_a_dir.write_text("text file!")

        with pytest.raises(FileExistsError):
            unpack_archive(
                archive_path=isolated_tgz_path.joinpath("simple.tgz"),
                destination=not_a_dir,
            )
