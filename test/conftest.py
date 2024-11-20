import json
import os
from pathlib import Path

import pytest
from click import testing as click_testing
from git.repo import Repo


@pytest.fixture
def cli_runner():
    yield click_testing.CliRunner()


@pytest.fixture(scope="function")
def no_github_token(set_environment_variables):
    token_value = os.environ["GITHUB_TOKEN"]
    del os.environ["GITHUB_TOKEN"]
    yield
    os.environ["GITHUB_TOKEN"] = token_value


@pytest.fixture(scope="session", autouse=True)
def set_environment_variables():
    old_environment = dict(os.environ)
    os.environ.clear()
    os.environ.update({"GITHUB_TOKEN": "ghp_test_value"})
    yield
    os.environ.clear()
    os.environ.update(old_environment)


@pytest.fixture(scope="function")
def example_github_repo(tmp_path):
    temp_repo = Repo.init(path=tmp_path, initial_branch="main")
    tmp_path.joinpath("test.txt").write_text("Sample file")
    temp_repo.index.add("test.txt")
    temp_repo.index.commit("Added test.txt")
    temp_repo.create_tag("0.1.0")
    yield temp_repo


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "unit" / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


@pytest.fixture
def base_path(tmp_path) -> str:
    return str(tmp_path)


@pytest.fixture
def fakeData_forPath():
    return {
        "a": {
            "b": {
                "c": "value"
            }
        }
    }