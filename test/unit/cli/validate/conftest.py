import os

import pytest
from faker import Faker
from git.repo import Repo

fake = Faker()


@pytest.fixture(scope="function")
def working_dir(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@pytest.fixture(scope="function")
def example_repo(working_dir):
    repo = Repo.init(path=working_dir)
    yield repo
