import pathlib

import pytest
from semver import Version

from launch.lib.local_repo import tags  # Used for mocking only
from launch.lib.local_repo.repo import acquire_repo
from launch.lib.local_repo.tags import (
    CommitNotTaggedException,
    CommitTagNotSemanticVersionException,
    create_version_tag,
    push_version_tag,
    read_semantic_tags,
    read_semantic_version_tag,
    read_tags,
    tag_is_semantic,
)


def test_acquire_repo(example_github_repo):
    acquired_repo = acquire_repo(repo_path=example_github_repo.working_dir)
    assert example_github_repo == acquired_repo


def test_get_tags(example_github_repo):
    example_github_repo.create_tag("not-semantic!")
    tags = read_tags(repo_path=example_github_repo.working_dir)
    assert len(tags) == 2
    assert "0.1.0" in tags
    assert "not-semantic!" in tags


def test_get_semantic_tags(example_github_repo):
    example_github_repo.create_tag("not-semantic!")
    tags = read_semantic_tags(repo_path=example_github_repo.working_dir)
    assert len(tags) == 1
    assert Version.parse("0.1.0") in tags


def test_create_version_tag(example_github_repo):
    new_version = Version(major=1, minor=2, patch=3)
    new_ref = create_version_tag(
        repo_path=example_github_repo.working_dir, version=new_version
    )
    assert new_ref.name == "1.2.3"


def test_push_version_tag(example_github_repo, mocker):
    # Since we don't really have a remote to push to, mocking is about all we can do.
    new_version = Version(major=1, minor=0, patch=0)
    new_ref = create_version_tag(
        repo_path=example_github_repo.working_dir, version=new_version
    )
    repo_mock = mocker.MagicMock()
    mocker.patch.object(tags, "acquire_repo", return_value=repo_mock)
    push_version_tag(repo_path=example_github_repo.working_dir, tag=new_ref)
    repo_mock.remote.assert_called_with("origin")
    repo_mock.remote.call_count == 2


@pytest.mark.parametrize(
    "tag_name, expected_outcome",
    [("1.2.3", True), ("not_semantic_version", False), ("0.1.0-prerelease", True)],
)
def test_tag_is_semantic(tag_name, expected_outcome, example_github_repo):
    tag = example_github_repo.create_tag(tag_name)
    assert tag_is_semantic(tag) == expected_outcome


def test_read_semantic_version_tag_head(example_github_repo):
    tag_version = read_semantic_version_tag(repo_path=example_github_repo.working_dir)
    assert tag_version == Version(major=0, minor=1, patch=0)


def test_read_semantic_version_tag_head_multiple(example_github_repo):
    new_version = Version(major=1, minor=2, patch=3)
    _ = create_version_tag(
        repo_path=example_github_repo.working_dir, version=new_version
    )
    tag_version = read_semantic_version_tag(repo_path=example_github_repo.working_dir)
    assert tag_version == new_version


def test_read_semantic_version_tag_head_no_tag(example_github_repo):
    pathlib.Path(example_github_repo.working_dir).joinpath("new.txt").write_text(
        "hello world"
    )
    example_github_repo.index.add("new.txt")
    example_github_repo.index.commit("Added new.txt")
    with pytest.raises(CommitNotTaggedException):
        read_semantic_version_tag(repo_path=example_github_repo.working_dir)


def test_read_semantic_version_tag_detached_head(example_github_repo):
    pathlib.Path(example_github_repo.working_dir).joinpath("new.txt").write_text(
        "hello world"
    )
    old_commit = example_github_repo.head.object
    example_github_repo.index.add("new.txt")
    example_github_repo.index.commit("Added new.txt")
    example_github_repo.create_tag("0.1.1")
    tag_version = read_semantic_version_tag(
        repo_path=example_github_repo.working_dir, commit=old_commit
    )
    assert tag_version == Version(major=0, minor=1, patch=0)


def test_read_semantic_version_tag_mixed_semver_and_not_semver(example_github_repo):
    example_github_repo.create_tag("not_semantic_versioned")
    tag_version = read_semantic_version_tag(repo_path=example_github_repo.working_dir)
    assert tag_version == Version(major=0, minor=1, patch=0)


def test_read_semantic_version_tag_not_semver(example_github_repo):
    pathlib.Path(example_github_repo.working_dir).joinpath("new.txt").write_text(
        "hello world"
    )
    example_github_repo.index.add("new.txt")
    example_github_repo.index.commit("Added new.txt")
    example_github_repo.create_tag("not_semantic_versioned")
    with pytest.raises(CommitTagNotSemanticVersionException):
        read_semantic_version_tag(repo_path=example_github_repo.working_dir)
