import pathlib
import pytest
import os
import shutil
from pathlib import Path
from unittest import mock
from launch.lib.service.template.functions import copy_template_files

@pytest.fixture
def setup_directories(tmp_path):
    src_dir = tmp_path / "src"
    target_dir = tmp_path / "target"
    src_dir.mkdir()
    target_dir.mkdir()
    (src_dir / "file1.txt").write_text("content1")
    (src_dir / "file2.txt").write_text("content2")
    (src_dir / "subdir").mkdir()
    (src_dir / "subdir" / "file3.txt").write_text("content3")
    return src_dir, target_dir

def test_copy_template_files_dry_run(setup_directories):
    src_dir, target_dir = setup_directories
    with mock.patch("click.secho") as mock_secho:
        copy_template_files(src_dir, target_dir, dry_run=True)
        mock_secho.assert_called_with(
            f"[DRYRUN] Processing template, would have copied files: {src_dir=} {target_dir=}",
            fg="yellow",
        )
    assert not any(target_dir.iterdir()), "Target directory should be empty in dry run"

def test_copy_template_files(setup_directories):
    src_dir, target_dir = setup_directories
    copy_template_files(src_dir, target_dir, dry_run=False)
    assert (target_dir / "file1.txt").exists()
    assert (target_dir / "file2.txt").exists()
    assert (target_dir / "subdir" / "file3.txt").exists()

def test_copy_template_files_not_platform(setup_directories):
    src_dir, target_dir = setup_directories
    copy_template_files(src_dir, target_dir, not_platform=True, dry_run=False)
    assert (target_dir / "file1.txt").exists()
    assert (target_dir / "file2.txt").exists()
    assert (target_dir / "subdir" / "file3.txt").exists()

def test_copy_template_files_overwrite_existing_files(setup_directories):
    src_dir, target_dir = setup_directories
    (src_dir / "file1.txt").write_text("old_content")
    copy_template_files(src_dir, target_dir, dry_run=False)
    assert (target_dir / "file1.txt").read_text() == "old_content"
    assert (target_dir / "file2.txt").read_text() == "content2"
    assert (target_dir / "subdir" / "file3.txt").read_text() == "content3"

def test_copy_template_files_handle_empty_source_directory(setup_directories):
    src_dir, target_dir = setup_directories
    shutil.rmtree(src_dir)
    src_dir.mkdir()
    copy_template_files(src_dir, target_dir, dry_run=False)
    assert not any(target_dir.iterdir()), "Target directory should be empty when source is empty"

def test_copy_template_files_handle_nonexistent_source_directory(setup_directories):
    src_dir, target_dir = setup_directories
    shutil.rmtree(src_dir)
    with pytest.raises(FileNotFoundError):
        copy_template_files(src_dir, target_dir, dry_run=False)

def test_copy_template_files_exclude_forbidden_directories(setup_directories):
    src_dir, target_dir = setup_directories
    forbidden_dir = src_dir / ".examples"
    forbidden_dir.mkdir()
    (forbidden_dir / "file4.txt").write_text("content4")
    with mock.patch("launch.constants.common.DISCOVERY_FORBIDDEN_DIRECTORIES", [".examples"]):
        copy_template_files(src_dir, target_dir, dry_run=False)
        assert not (target_dir / ".examples").exists()
        assert (target_dir / "file1.txt").exists()
        assert (target_dir / "file2.txt").exists()
        assert (target_dir / "subdir" / "file3.txt").exists()