import itertools
import logging

from semver import Version

logger = logging.getLogger(__name__)

BRANCH_DELIMITER = "/"

PATCH_NAME_PARTS = ["fix", "bug", "patch", "dependabot"]
MINOR_NAME_PARTS = ["feature"]
MAJOR_NAME_PARTS = []

ALL_NAME_PARTS = list(
    itertools.chain(MAJOR_NAME_PARTS, MINOR_NAME_PARTS, PATCH_NAME_PARTS)
)

BREAKING_CHARS = ["!"]
CAPITALIZE_FIRST_IS_BREAKING = True
DEFAULT_VERSION = Version(major=1, minor=0, patch=0)


class ChangeType:
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class InvalidBranchNameException(Exception):
    pass


def split_delimiter(branch_name: str, delimiter: str | None = None) -> tuple[str, str]:
    if not delimiter:
        delimiter = BRANCH_DELIMITER

    separated = branch_name.split(sep=delimiter)
    if not len(separated) >= 2:
        raise InvalidBranchNameException(
            f"Branch name {branch_name} did not contain expected delimiter {delimiter}"
        )
    return separated[0], delimiter.join(separated[1:])


def latest_tag(tags: list[Version]) -> Version:
    return sorted(tags)[-1]


def validate_name(branch_name: str) -> bool:
    """Checks the contents of a branch name against this module's configuration and returns a success/failure boolean with the outcome.

    Args:
        branch_name (str): Name of the branch to validate.

    Returns:
        bool: Success indicator. A True value indicates that this branch name conforms to the expected convention, a False value indicates otherwise.
    """
    try:
        revision_type, _ = split_delimiter(branch_name=branch_name)
    except InvalidBranchNameException:
        return False

    for breaking_char in BREAKING_CHARS:
        if breaking_char in revision_type:
            revision_type = revision_type.replace(breaking_char, "")

    if revision_type.lower().strip() not in map(str.lower, ALL_NAME_PARTS):
        return False
    return True


def predict_version(
    existing_tags: list[Version],
    branch_name: str,
    breaking_chars: list[str] | None = None,
    capitalize_first_is_breaking: bool | None = None,
) -> Version:
    if not len(existing_tags):
        logger.warning(f"No tags exist on this repo, defaulting to {DEFAULT_VERSION}")
        return DEFAULT_VERSION

    latest_version = latest_tag(tags=existing_tags)
    logger.debug(f"Got {latest_version=} as the latest tag")
    predicted_change_type = predict_change_type(
        branch_name=branch_name,
        breaking_chars=breaking_chars,
        capitalize_first_is_breaking=capitalize_first_is_breaking,
    )
    match predicted_change_type:
        case ChangeType.MAJOR:
            return latest_version.bump_major()
        case ChangeType.MINOR:
            return latest_version.bump_minor()
        case ChangeType.PATCH:
            return latest_version.bump_patch()
        case _:
            raise ValueError(
                f"Unexpected change type predicted: {predicted_change_type=}"
            )


def predict_change_type(
    branch_name: str,
    breaking_chars: list[str] | None = None,
    capitalize_first_is_breaking: bool | None = None,
) -> ChangeType:
    breaking_change: bool = False

    if not breaking_chars:
        breaking_chars = BREAKING_CHARS

    if capitalize_first_is_breaking is None:
        capitalize_first_is_breaking = CAPITALIZE_FIRST_IS_BREAKING

    revision_type, _ = split_delimiter(branch_name=branch_name)

    logger.debug(f"Evaluating {revision_type=} against {ALL_NAME_PARTS=}")

    for breaking_char in breaking_chars:
        if breaking_char in revision_type:
            logger.debug(
                f"Detected {breaking_char=} in branch name, setting {breaking_change=}"
            )
            breaking_change = True
            revision_type = revision_type.replace(breaking_char, "")

    if revision_type.lower().strip() not in map(str.lower, ALL_NAME_PARTS):
        raise InvalidBranchNameException(
            f"Branch name {branch_name} is invalid, must case-insensitively match one of {ALL_NAME_PARTS}"
        )

    if capitalize_first_is_breaking:
        if revision_type[0] == revision_type[0].upper():
            logger.debug(
                f"Revision begins with a capital letter, setting {breaking_change=}"
            )
            breaking_change = True

    if breaking_change or revision_type.lower().strip() in MAJOR_NAME_PARTS:
        return ChangeType.MAJOR
    elif revision_type.lower().strip() in MINOR_NAME_PARTS:
        return ChangeType.MINOR
    else:
        return ChangeType.PATCH
