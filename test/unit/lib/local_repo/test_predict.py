from contextlib import ExitStack as does_not_raise

import pytest
from semver import Version

from launch.lib.local_repo.predict import (
    ChangeType,
    InvalidBranchNameException,
    latest_tag,
    predict_change_type,
    predict_version,
    split_delimiter,
)


@pytest.mark.parametrize(
    "branch_name, delimiter, expected_outcome, raises",
    [
        ("", None, None, pytest.raises(InvalidBranchNameException)),
        ("test/branch", None, ("test", "branch"), does_not_raise()),
        ("test/branch/compound", None, ("test", "branch/compound"), does_not_raise()),
        ("alternate#delimiter", "#", ("alternate", "delimiter"), does_not_raise()),
        (
            "alternate#delimiter#compound",
            "#",
            ("alternate", "delimiter#compound"),
            does_not_raise(),
        ),
        ("nonexistent/delimiter", "#", None, pytest.raises(InvalidBranchNameException)),
    ],
)
def test_split_delimiter(
    branch_name: str, delimiter: str, expected_outcome: tuple[str, str] | None, raises
):
    with raises:
        assert expected_outcome == split_delimiter(
            branch_name=branch_name, delimiter=delimiter
        )


def test_latest_tag():
    raw_versions = ["0.1.0", "0.1.1", "0.1.1-prerelease", "0.2.0", "1.0.0"]

    latest = latest_tag([Version.parse(r) for r in raw_versions])
    assert latest == Version.parse("1.0.0")


@pytest.mark.parametrize(
    "branch_name, expected_change_type, raises",
    (
        ["fix/should-patch", ChangeType.PATCH, does_not_raise()],
        ["bug/should-patch", ChangeType.PATCH, does_not_raise()],
        ["patch/should-patch", ChangeType.PATCH, does_not_raise()],
        ["dependabot/should-patch", ChangeType.PATCH, does_not_raise()],
        ["feature/should-minor", ChangeType.MINOR, does_not_raise()],
        ["fix!/breaking-char-should-major", ChangeType.MAJOR, does_not_raise()],
        ["Fix/breaking-cap-should-major", ChangeType.MAJOR, does_not_raise()],
        ["bad/name", None, pytest.raises(InvalidBranchNameException)],
        ["bad_name", None, pytest.raises(InvalidBranchNameException)],
        ["feat/is-not-valid-anymore", None, pytest.raises(InvalidBranchNameException)],
        [
            "release/is-not-valid-anymore",
            None,
            pytest.raises(InvalidBranchNameException),
        ],
    ),
)
def test_predict_change_type(
    branch_name: str, expected_change_type: ChangeType, raises
):
    with raises:
        assert predict_change_type(branch_name=branch_name) == expected_change_type


@pytest.mark.parametrize(
    "branch_name, expected_version, raises",
    (
        ["fix/should-patch", Version(1, 0, 1), does_not_raise()],
        ["bug/should-patch", Version(1, 0, 1), does_not_raise()],
        ["patch/should-patch", Version(1, 0, 1), does_not_raise()],
        ["dependabot/should-patch", Version(1, 0, 1), does_not_raise()],
        ["feature/should-minor", Version(1, 1, 0), does_not_raise()],
        ["fix!/breaking-char-should-major", Version(2, 0, 0), does_not_raise()],
        ["Fix/breaking-cap-should-major", Version(2, 0, 0), does_not_raise()],
        ["bad/name", Version(2, 0, 0), pytest.raises(InvalidBranchNameException)],
        ["bad_name", Version(2, 0, 0), pytest.raises(InvalidBranchNameException)],
        ["feat/is-not-valid-anymore", None, pytest.raises(InvalidBranchNameException)],
        [
            "release/is-not-valid-anymore",
            None,
            pytest.raises(InvalidBranchNameException),
        ],
    ),
)
def test_predict(branch_name: str, expected_version: Version, raises):
    raw_tags = ["0.1.0", "0.1.1", "0.1.1-prerelease", "0.2.0", "1.0.0"]
    existing_tags = [Version.parse(r) for r in raw_tags]

    with raises:
        new_version = predict_version(
            existing_tags=existing_tags, branch_name=branch_name
        )
        assert new_version == expected_version


@pytest.mark.parametrize(
    "branch_name", ["fix/no-tags-yet", "feature/no-tags-yet", "patch!/no-tags-yet"]
)
def test_predict_default_version(branch_name: str):
    existing_tags = []
    expected_version = Version(1, 0, 0)
    new_version = predict_version(existing_tags=existing_tags, branch_name=branch_name)
    assert new_version == expected_version
