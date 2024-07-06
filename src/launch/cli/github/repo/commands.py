import logging
import sys

import click
import git
from git.repo import Repo
from github.GithubException import UnknownObjectException

from launch.config.github import GITHUB_ORG_NAME
from launch.lib.github.auth import get_github_instance
from launch.lib.github.labels import (
    create_custom_labels,
    get_label_for_change_type,
    has_custom_labels,
)
from launch.lib.github.repo import create_repository
from launch.lib.local_repo.predict import (
    InvalidBranchNameException,
    predict_change_type,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option("--repository-url", required=True, help="Repository url to clone.")
@click.option(
    "--target",
    help="The target directory to clone the repository into.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def clone(
    repository_url: str,
    target: str,
    dry_run: bool,
):
    """Clones a single repository."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be cloned", fg="yellow")

    try:
        logger.info(f"Attempting to clone repository: {repository_url} into {target}")
        repository = Repo.clone_from(repository_url, target)
        logger.info(f"Repository {repository_url} cloned successfully to {target}")
    except git.GitCommandError as e:
        logger.error(
            f"Error occurred while cloning the repository: {repository_url}, Error: {e}"
        )
        raise RuntimeError(
            f"An error occurred while cloning the repository: {repository_url}"
        ) from e
    return repository


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization containing your repository. Defaults to the {GITHUB_ORG_NAME} organization.",
)
@click.option("--name", required=True, help="The name of the repository.")
@click.option(
    "--description",
    default="Service created with launch-cli.",
    help="A short description of the repository.",
)
@click.option(
    "--public",
    is_flag=True,
    default=False,
    help="The visibility of the repository.",
)
@click.option(
    "--visibility",
    default="private",
    help="The visibility of the repository. Can be one of: public, private ",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def create(
    organization: str,
    name: str,
    description: str,
    public: bool,
    visibility: str,
    dry_run: bool,
):
    """Creates a single repository."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be created in GitHub", fg="yellow"
        )

    g = get_github_instance()
    create_repository(
        g=g,
        organization=organization,
        name=name,
        description=description,
        public=public,
        visibility=visibility,
    )


@click.command()
@click.option("--repository-name", required=True)
@click.option("--organization", default=GITHUB_ORG_NAME)
def check_labels(repository_name: str, organization: str):
    """Check a repository to see if it has all of the custom labels we expect for GitHub Actions.
    If the repository is missing labels, a non-zero error code will be returned!"""
    g = get_github_instance()
    repo = g.get_repo(full_name_or_id=f"{organization}/{repository_name}")
    if not has_custom_labels(repository=repo):
        sys.exit(1)


@click.command()
@click.option("--repository-name", required=True)
@click.option("--organization", default=GITHUB_ORG_NAME)
def create_labels(repository_name: str, organization: str):
    """Creates custom labels for GitHub Actions on a repository. If the repository has all the
    expected labels, this will return successfully with a message showing zero labels created,
    allowing this command to be safely rerun against a repository multiple times."""
    repo_full_name = f"{organization}/{repository_name}"
    g = get_github_instance()
    repo = g.get_repo(full_name_or_id=repo_full_name)
    labels_created = create_custom_labels(repository=repo)
    logger.info(f"Created {labels_created} new labels on {repo_full_name}.")


@click.command()
@click.option("--repository-name", required=True)
@click.option(
    "--pull-request-id", type=click.INT, required=True, help="Pull Request ID to label"
)
@click.option("--organization", default=GITHUB_ORG_NAME)
def label_pull_request(repository_name: str, pull_request_id: int, organization: str):
    """Applies labels to a GitHub pull request based on the predicted next version from the branch name."""
    repo_full_name = f"{organization}/{repository_name}"

    try:
        g = get_github_instance()
        repo = g.get_repo(full_name_or_id=repo_full_name)
    except UnknownObjectException:
        logger.error(
            f"Failed to retrieve repository {repo_full_name}. Check for existence and access!"
        )
        sys.exit(1)
    try:
        pr = repo.get_pull(number=pull_request_id)
    except UnknownObjectException:
        logger.error(
            f"Failed to retrieve pull request #{pull_request_id} from {repo_full_name}. Check for existence and access!"
        )
        sys.exit(2)

    pr_branch_name = pr.head.ref
    try:
        predicted_change_type = predict_change_type(branch_name=pr_branch_name)
    except InvalidBranchNameException as e:
        logger.error(f"Failure when predicting change type: {e}")
        sys.exit(3)

    try:
        label_to_add = get_label_for_change_type(
            repository=repo, change_type=predicted_change_type
        )
        pr.add_to_labels(label_to_add)
    except Exception as e:
        logger.error(f"Failed to add labels to {repo_full_name}#{pull_request_id}: {e}")
        sys.exit(4)
