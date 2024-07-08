import pytest

from launch.lib.service.common import callback_create_directories


@pytest.fixture
def base_directory(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    return base


def test_callback_create_directories_with_dict_value(base_directory):
    key = "new_directory"
    value = {}
    base_path = base_directory
    current_path = "current"

    assert (
        callback_create_directories(
            key, value, base_path=str(base_path), current_path=current_path
        )
        is False
    )
    assert (base_path / current_path / key).exists()


def test_callback_create_directories_with_non_dict_value(base_directory):
    key = "should_not_matter"
    value = "some_value"
    base_path = base_directory
    current_path = "current"

    assert (
        callback_create_directories(
            key, value, base_path=str(base_path), current_path=current_path
        )
        is True
    )
    assert not (base_path / current_path / key).exists()
    assert (base_path / current_path).exists()
