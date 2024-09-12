from dataclasses import dataclass
from enum import StrEnum

from github import Github
from github.CommitStatus import CommitStatus


class CommitStatusState(StrEnum):
    error = "error"
    failure = "failure"
    pending = "pending"
    success = "success"


@dataclass
class CommitStatusUpdatePayload:
    state: CommitStatusState
    target_url: str
    description: str
    context: str


def get_commit_status(
    git_connection: Github, repo_name: str, repo_org: str, commit_sha: str, context: str
) -> CommitStatus | None:
    repo = git_connection.get_repo(full_name_or_id=f"{repo_org}/{repo_name}")
    commit = repo.get_commit(sha=commit_sha)
    commit_statuses = commit.get_combined_status().statuses
    filtered_by_context = list(filter(lambda x: x.context == context, commit_statuses))
    if len(filtered_by_context) > 1:
        raise RuntimeError(f"Too many filtered items! {filtered_by_context}")
    elif len(filtered_by_context) == 1:
        return filtered_by_context[0]
    else:
        return None


def set_commit_status(
    git_connection: Github,
    repo_name: str,
    repo_org: str,
    commit_sha: str,
    payload: CommitStatusUpdatePayload,
) -> None:
    repo = git_connection.get_repo(full_name_or_id=f"{repo_org}/{repo_name}")
    commit = repo.get_commit(sha=commit_sha)
    commit.create_status(
        state=payload.state,
        target_url=str(payload.target_url),
        description=payload.description,
        context=payload.context,
    )
