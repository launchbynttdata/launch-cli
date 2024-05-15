import logging

import pytest
from github.GithubException import GithubException
from github.Label import Label
from semver import Version

from launch.github import tags
from launch.github.labels import CUSTOM_LABELS, create_custom_labels, has_custom_labels


@pytest.fixture
def mocked_repository(mocker):
    mocked_repo = mocker.MagicMock()
    mocked_repo.name = "mocked_repo"
    yield mocked_repo


class TestHasCustomLabels:
    def test_has_custom_labels_no_labels(self, mocked_repository):
        mocked_repository.get_labels.return_value = []
        assert not has_custom_labels(repository=mocked_repository)

    def test_has_custom_labels_some_labels(self, mocked_repository):
        mocked_repository.get_labels.return_value = [CUSTOM_LABELS[0]]
        assert not has_custom_labels(repository=mocked_repository)

    def test_has_custom_labels_all_labels(self, mocked_repository):
        mocked_repository.get_labels.return_value = CUSTOM_LABELS
        assert has_custom_labels(repository=mocked_repository)


class TestCreateCustomLabels:
    def test_create_custom_labels(self, mocked_repository, mocker):
        expected_calls = []
        for custom_label in CUSTOM_LABELS:
            expected_calls.append(
                mocker.call(
                    name=custom_label.name,
                    color=custom_label.color,
                    description=custom_label.description,
                )
            )

        num_created = create_custom_labels(repository=mocked_repository)
        mocked_repository.create_label.assert_has_calls(expected_calls)

        assert num_created == len(CUSTOM_LABELS)
        assert mocked_repository.create_label.call_count == len(CUSTOM_LABELS)

    def test_create_custom_labels_already_exist(self, mocked_repository, mocker):
        mocked_repository.create_label.side_effect = GithubException(
            status=422, data={"errors": [{"code": "already_exists"}]}
        )

        expected_calls = []
        for custom_label in CUSTOM_LABELS:
            expected_calls.append(
                mocker.call(
                    name=custom_label.name,
                    color=custom_label.color,
                    description=custom_label.description,
                )
            )

        num_created = create_custom_labels(repository=mocked_repository)
        mocked_repository.create_label.assert_has_calls(expected_calls)

        assert num_created == 0
        assert mocked_repository.create_label.call_count == len(CUSTOM_LABELS)
