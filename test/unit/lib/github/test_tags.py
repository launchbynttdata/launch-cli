import logging

import pytest
from semver import Version

from launch.lib.github import tags


@pytest.fixture
def mocked_tags(mocker):
    semantic_tag = mocker.MagicMock()
    semantic_tag.name = "1.2.3"

    semantic_prerelease_tag = mocker.MagicMock()
    semantic_prerelease_tag.name = "1.2.3-alpha"

    bare_tag = mocker.MagicMock()
    bare_tag.name = "foo"

    slash_tag = mocker.MagicMock()
    slash_tag.name = "tag/with/slashes"

    dash_tag = mocker.MagicMock()
    dash_tag.name = "hello-world"
    yield [semantic_tag, semantic_prerelease_tag, bare_tag, slash_tag, dash_tag]


def test_get_repo_tags_includes_non_semantic_versions(mocked_tags, caplog, mocker):
    expected_tags = mocked_tags

    mocked_repo = mocker.MagicMock()
    mocked_repo.name = "mocked_repo"
    mocked_repo.get_tags.return_value = mocked_tags

    with caplog.at_level(logging.DEBUG):
        returned_tags = tags.get_repo_tags(repo=mocked_repo)
        assert (
            f"Fetched {len(expected_tags)} tags from {mocked_repo.name}" in caplog.text
        )
        assert returned_tags == expected_tags


def test_get_repo_semantic_versions_drops_non_semantic(mocked_tags, caplog, mocker):
    input_tags = mocked_tags
    expected_tags = [Version(1, 2, 3), Version(1, 2, 3, "alpha")]

    mocked_repo = mocker.MagicMock()
    mocked_repo.name = "mocked_repo"
    mocked_repo.get_tags.return_value = input_tags

    with caplog.at_level(logging.DEBUG):
        returned_tags = tags.get_repo_semantic_versions(repo=mocked_repo)
        assert f"Fetched {len(input_tags)} tags from {mocked_repo.name}" in caplog.text
        assert "foo is not valid SemVer string" in caplog.text
        assert (
            f"Successfully parsed {len(expected_tags)} from tags on {mocked_repo.name}"
            in caplog.text
        )
        assert all([r in expected_tags for r in returned_tags])
