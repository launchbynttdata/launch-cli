import json
from pathlib import Path

import pytest

from launch.constants.common import BUILD_DEPENDENCIES_DIR
from launch.lib.service.common import callback_copy_properties_files


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


@pytest.fixture
def setup_file_structure(fakedata, tmp_path):
    base_path = str(tmp_path) + "/base/"
    current_path = "current/path"
    (Path(base_path) / current_path).mkdir(parents=True, exist_ok=True)

    properties_file_path = Path(base_path) / fakedata["file"]
    properties_file_path.touch()

    return base_path, current_path


def test_callback_copy_properties_files_no_dict(fakedata, setup_file_structure):
    base_path, current_path = setup_file_structure

    kwargs = {
        "base_path": base_path,
        "current_path": Path(current_path),
        "nested_dict": {},
    }

    result = callback_copy_properties_files(fakedata["key"], fakedata["file"], **kwargs)
    expected_dest_path = Path(base_path) / current_path / "terraform.tfvars"

    assert expected_dest_path.exists()
    assert "properties_file" in result
    assert (
        result["properties_file"]
        == f"{BUILD_DEPENDENCIES_DIR}/{current_path}/terraform.tfvars"
    )


def test_callback_copy_properties_files_with_uuid(fakedata, setup_file_structure):
    base_path, current_path = setup_file_structure
    kwargs = {
        "base_path": base_path,
        "current_path": Path(current_path),
        "nested_dict": {},
        "uuid": True,
    }

    result = callback_copy_properties_files(fakedata["key"], fakedata["file"], **kwargs)
    assert "uuid" in result
    assert len(result["uuid"]) == 6


def test_callback_copy_properties_files_with_dict_value(fakedata, setup_file_structure):
    base_path, current_path = setup_file_structure
    kwargs = {
        "base_path": base_path,
        "current_path": current_path,
        "nested_dict": {},
    }

    result = callback_copy_properties_files(fakedata["key"], {}, **kwargs)
    assert result == None
