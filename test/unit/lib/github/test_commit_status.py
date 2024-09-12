import pytest
from faker import Faker
from github.CommitStatus import CommitStatus

from launch.lib.github.commit_status import (
    CommitStatusState,
    CommitStatusUpdatePayload,
    get_commit_status,
    set_commit_status,
)

fake = Faker()


@pytest.fixture()
def context_words():
    yield {
        "context_word": fake.unique.word(),
        "context_nonmatching_word": fake.unique.word(),
    }


@pytest.fixture
def repo_and_commit_attributes():
    yield {
        "org_name": fake.unique.word(),
        "repo_name": fake.unique.word(),
        "commit_sha": fake.sha1(),
    }


@pytest.fixture
def mocked_github(mocker):
    github_instance = mocker.MagicMock()
    repo_instance = mocker.MagicMock()
    commit_instance = mocker.MagicMock()
    combined_status_instance = mocker.MagicMock()

    github_instance.get_repo.return_value = repo_instance
    repo_instance.get_commit.return_value = commit_instance
    commit_instance.get_combined_status.return_value = combined_status_instance

    yield {
        "github_instance": github_instance,
        "repo_instance": repo_instance,
        "commit_instance": commit_instance,
        "combined_status_instance": combined_status_instance,
    }


def test_get_commit_status(
    mocker, mocked_github, repo_and_commit_attributes, context_words
):
    matching_context_status = mocker.MagicMock(spec=CommitStatus)
    matching_context_status.context = context_words["context_word"]

    nonmatching_context_status = mocker.MagicMock(spec=CommitStatus)
    nonmatching_context_status.context = context_words["context_nonmatching_word"]

    mocked_github["combined_status_instance"].statuses = [
        matching_context_status,
        nonmatching_context_status,
    ]

    found_status = get_commit_status(
        git_connection=mocked_github["github_instance"],
        repo_name=repo_and_commit_attributes["repo_name"],
        repo_org=repo_and_commit_attributes["org_name"],
        commit_sha=repo_and_commit_attributes["commit_sha"],
        context=context_words["context_word"],
    )

    expected_repo_path = f"{repo_and_commit_attributes['org_name']}/{repo_and_commit_attributes['repo_name']}"

    mocked_github["github_instance"].get_repo.assert_called_once_with(
        full_name_or_id=expected_repo_path
    )
    mocked_github["repo_instance"].assert_called_once_with(
        sha=repo_and_commit_attributes["commit_sha"]
    )
    assert mocked_github["commit_instance"].get_combined_status.called_once()
    assert found_status.context == context_words["context_word"]


def test_get_commit_status_no_context_match(
    mocker, mocked_github, repo_and_commit_attributes, context_words
):
    nonmatching_context_status = mocker.MagicMock(spec=CommitStatus)
    nonmatching_context_status.context = context_words["context_nonmatching_word"]

    mocked_github["combined_status_instance"].statuses = [nonmatching_context_status]

    found_status = get_commit_status(
        git_connection=mocked_github["github_instance"],
        repo_name=repo_and_commit_attributes["repo_name"],
        repo_org=repo_and_commit_attributes["org_name"],
        commit_sha=repo_and_commit_attributes["commit_sha"],
        context=context_words["context_word"],
    )

    expected_repo_path = f"{repo_and_commit_attributes['org_name']}/{repo_and_commit_attributes['repo_name']}"

    mocked_github["github_instance"].get_repo.assert_called_once_with(
        full_name_or_id=expected_repo_path
    )
    mocked_github["repo_instance"].get_commit.assert_called_once_with(
        sha=repo_and_commit_attributes["commit_sha"]
    )
    assert mocked_github["commit_instance"].get_combined_status.called_once()
    assert found_status is None


def test_set_commit_status(mocker, mocked_github, repo_and_commit_attributes):
    payload = CommitStatusUpdatePayload(
        state=CommitStatusState.success,
        target_url=fake.url(),
        description=fake.sentence(),
        context=fake.word(),
    )

    set_commit_status(
        git_connection=mocked_github["github_instance"],
        repo_name=repo_and_commit_attributes["repo_name"],
        repo_org=repo_and_commit_attributes["org_name"],
        commit_sha=repo_and_commit_attributes["commit_sha"],
        payload=payload,
    )

    expected_repo_path = f"{repo_and_commit_attributes['org_name']}/{repo_and_commit_attributes['repo_name']}"

    mocked_github["github_instance"].get_repo.assert_called_once_with(
        full_name_or_id=expected_repo_path
    )
    mocked_github["repo_instance"].get_commit.assert_called_once_with(
        sha=repo_and_commit_attributes["commit_sha"]
    )
    mocked_github["commit_instance"].create_status.assert_called_once_with(
        state=payload.state,
        target_url=str(payload.target_url),
        description=payload.description,
        context=payload.context,
    )
