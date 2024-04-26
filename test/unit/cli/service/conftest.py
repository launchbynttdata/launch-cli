import json
import os
from pathlib import Path
from random import choice, randint
from typing import Generator

import pytest
from faker import Faker

from launch.cli.service.commands import create_no_git

fake = Faker()


@pytest.fixture(scope="function")
def fake_organization_name():
    return "-".join(fake.words(nb=randint(1, 3)))


@pytest.fixture(scope="function")
def fake_repo_name():
    providers = ["aws", "azurerm", "azureado", "sumologic"]
    module_type = ["primitive", "library", "collection", "reference"]
    resource_name = "-".join(fake.words(nb=randint(1, 3)))
    return f"tf-{choice(providers)}-module_{choice(module_type)}-{resource_name}"


@pytest.fixture(scope="function")
def fake_module_git_url(fake_organization_name, fake_repo_name):
    return f"https://github.com/{fake_organization_name}/{fake_repo_name}.git"


@pytest.fixture(scope="function")
def service_path(tmp_path) -> Generator[Path, None, None]:
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@pytest.fixture(scope="function")
def service_inputs_file(
    service_path, fake_module_git_url
) -> Generator[Path, None, None]:
    inputs = {
        "sources": {"service": {"module": fake_module_git_url, "tag": "1.0.0"}},
        "provider": "az",
        "accounts": {"sandbox": "d34db33f-a1b2-c3d4-e5f6-0d3c4fc0ff33"},
        "naming_prefix": "acr",
        "platform": {
            "service": {
                "sandbox": {
                    "eastus": {
                        "000": {"properties_file": f"{service_path}/vars.tfvars"}
                    }
                }
            }
        },
    }
    service_path.joinpath("inputs.json").write_text(json.dumps(inputs, indent=2))
    yield service_path.joinpath("inputs.json")


@pytest.fixture(scope="function")
def service_vars_file(service_path) -> Generator[Path, None, None]:
    vars_contents = """resource_group_name     = "dso-k8s-001"
location                = "useast"
container_registry_name = "launch-dso-public"
sku                     = "Standard"
admin_enabled           = false
tags = {
  environment = "sandbox"
  owner       = "Debasish"
  Purpose     = "ACR for common DSO container images"
}
"""
    service_path.joinpath("vars.tfvars").write_text(vars_contents)
    yield service_path.joinpath("vars.tfvars")


@pytest.fixture(scope="function")
def initialized_repo(
    cli_runner, service_path, service_inputs_file, service_vars_file
) -> Generator[Path, None, None]:
    cli_runner.invoke(
        create_no_git,
        ["--name", "acr_test", "--in-file", str(service_inputs_file.absolute())],
    )
    yield service_path
