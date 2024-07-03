from dataclasses import dataclass

from github.GithubException import GithubException
from github.Label import Label
from github.Repository import Repository

from launch.lib.local_repo.predict import ChangeType


@dataclass
class CustomLabel:
    name: str
    color: str
    description: str


CUSTOM_LABELS = [
    CustomLabel(
        name="dependencies",
        color="0366d6",
        description="Pull requests that update a dependency file",
    ),
    CustomLabel(
        name="breaking",
        color="b60205",
        description="Pull requests that contain a breaking change",
    ),
]


CHANGE_TYPE_LABEL_MAP: dict[ChangeType, str] = {
    ChangeType.MAJOR: "breaking",
    ChangeType.MINOR: "enhancement",
    ChangeType.PATCH: "bug",
}


def get_label_for_change_type(repository: Repository, change_type: ChangeType) -> Label:
    return repository.get_label(name=CHANGE_TYPE_LABEL_MAP[change_type])


def has_custom_labels(
    repository: Repository, custom_labels: list[CustomLabel] = None
) -> bool:
    """Determines whether a repository has all the custom labels that we expect.

    Args:
        repository (Repository): GitHub Repository
        custom_labels (list[CustomLabel], optional): List of labels to check. Defaults to None, which will pull the standard custom labels from the module.

    Returns:
        bool: True if all expected custom labels were found, False otherwise.
    """
    if not custom_labels:
        custom_labels = CUSTOM_LABELS
    all_labels = [label for label in repository.get_labels()]
    return all(
        [
            custom_label.name in [label.name for label in all_labels]
            for custom_label in custom_labels
        ]
    )


def create_custom_labels(
    repository: Repository, custom_labels: list[CustomLabel] = None
) -> int:
    """Creates custom labels on a given GitHub repository, returning the number of labels that were created.
    This can be run many times against the same repository without creating problems.

    Args:
        repository (Repository): GitHub Repository
        custom_labels (list[CustomLabel], optional): List of labels to create. Defaults to None, which will pull the standard custom labels from the module.

    Returns:
        int: Number of labels created.
    """
    if not custom_labels:
        custom_labels = CUSTOM_LABELS
    num_created = 0
    for custom_label in custom_labels:
        try:
            repository.create_label(
                name=custom_label.name,
                color=custom_label.color.strip("#"),
                description=custom_label.description.strip(),
            )
            num_created += 1
        except GithubException as ghe:
            if "already_exists" in ghe._GithubException__data.get("errors", [{}])[
                0
            ].get("code", ""):
                pass
            else:
                raise
    return num_created
