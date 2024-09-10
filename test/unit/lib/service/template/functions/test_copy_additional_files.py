import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from launch.config.common import BUILD_TEMP_DIR_PATH, PLATFORM_SRC_DIR_PATH
from launch.lib.service.template.launchconfig import LaunchConfigTemplate


@pytest.fixture(scope="class")
def launch_config_file_contents():
    yield {
        "provider": "aws",
        "accounts": {"root": "launch-root-admin"},
        "naming_prefix": "unit-test",
        "skeleton": {
            "url": "https://github.com/launchbynttdata/lcaf-template-terragrunt.git",
            "tag": "1.0.0",
        },
        "sources": {
            "service": {
                "url": "https://github.com/launchbynttdata/tf-aws-module_collection-codepipeline.git",
                "tag": "1.0.2",
            },
            "pipeline": {
                "url": "https://github.com/launchbynttdata/tf-aws-module_collection-codepipeline.git",
                "tag": "1.0.2",
            },
            "webhook": {
                "url": "https://github.com/launchbynttdata/tf-aws-module_reference-bulk_lambda_function.git",
                "tag": "1.1.0",
            },
        },
        "platform": {
            "service": {
                "root": {
                    "us-east-2": {
                        "000": {
                            "properties_file": "./platform/service/root/us-east-2/000/terraform.tfvars",
                            "additional_files": {
                                "root_file.txt": "./root_file.txt",
                                "renamed_file.txt": "./platform/service/root/us-east-2/000/environment_file.txt",
                                "environment_file.txt": "./platform/service/root/us-east-2/000/environment_file.txt",
                                "nested_rename/renamed_file.txt": "./platform/service/root/us-east-2/000/environment_file.txt",
                            },
                        }
                    }
                }
            },
            "pipeline": {
                "pipeline-provider": {
                    "root": {
                        "us-east-2": {
                            "000": {
                                "properties_file": "./platform/pipeline/pipeline-provider/root/us-east-2/000/terraform.tfvars"
                            }
                        }
                    }
                },
                "webhook-provider": {
                    "root": {
                        "us-east-2": {
                            "000": {
                                "properties_file": "./platform/pipeline/webhook-provider/root/us-east-2/000/terraform.tfvars"
                            }
                        }
                    }
                },
            },
        },
    }


@pytest.fixture(scope="class")
def launch_service_directory(launch_config_file_contents):
    old_work_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as work_dir:
        work_path = Path(work_dir)
        work_path.joinpath(".launch_config").write_text(
            json.dumps(launch_config_file_contents)
        )
        work_path.joinpath("root_file.txt").write_text("root file")
        environment_file = (
            work_path.joinpath("platform")
            .joinpath("service")
            .joinpath("root")
            .joinpath("us-east-2")
            .joinpath("000")
            .joinpath("environment_file.txt")
        )
        environment_file.parent.mkdir(parents=True, exist_ok=False)
        environment_file.write_text("environment file")
        os.chdir(work_dir)
        yield work_path
    os.chdir(old_work_dir)


@pytest.fixture(scope="class")
def built_dir(launch_service_directory, launch_config_file_contents):
    config = launch_config_file_contents[PLATFORM_SRC_DIR_PATH]
    target_dir = launch_service_directory.joinpath(BUILD_TEMP_DIR_PATH).joinpath(
        Path.cwd().name
    )
    LaunchConfigTemplate(dry_run=False).copy_additional_files(
        value=config["service"]["root"]["us-east-2"]["000"],
        current_path=(
            target_dir.joinpath("platform")
            .joinpath("service")
            .joinpath("root")
            .joinpath("us-east-2")
            .joinpath("000")
        ),
        repo_base=launch_service_directory,
        dest_base=target_dir,
    )
    yield launch_service_directory


class TestCopyAdditionalFiles:
    def test_additional_environment_file_lands_in_environment(self, built_dir):
        """The default use case, in which we copy a file with a given numbered environment into the build structure as-is."""
        build_path = built_dir.joinpath(BUILD_TEMP_DIR_PATH).joinpath(Path.cwd().name)
        expected_environment_file_path = build_path.joinpath(
            "platform/service/root/us-east-2/000/environment_file.txt"
        )
        assert expected_environment_file_path.exists()
        assert expected_environment_file_path.is_file()
        assert expected_environment_file_path.read_text() == "environment file"

    def test_copy_additional_file_allows_rename(self, built_dir):
        """Copying files allows for a rename of the file by adjusting the key in the platform config."""
        build_path = built_dir.joinpath(BUILD_TEMP_DIR_PATH).joinpath(Path.cwd().name)
        expected_renamed_file_path = build_path.joinpath(
            "platform/service/root/us-east-2/000/renamed_file.txt"
        )
        assert expected_renamed_file_path.exists()
        assert expected_renamed_file_path.is_file()
        assert expected_renamed_file_path.read_text() == "environment file"

    def test_copy_additional_file_nested_directory(self, built_dir):
        """Copying files allows for nesting files in arbitrary subdirectories by putting the path in the key."""
        build_path = built_dir.joinpath(BUILD_TEMP_DIR_PATH).joinpath(Path.cwd().name)
        expected_nested_file_path = build_path.joinpath(
            "platform/service/root/us-east-2/000/nested_rename/renamed_file.txt"
        )
        assert expected_nested_file_path.exists()
        assert expected_nested_file_path.is_file()
        assert expected_nested_file_path.read_text() == "environment file"

    def test_copy_additional_file_from_root(self, built_dir):
        """Allows for copying a shared file located in the root of the repository into the numbered environment."""
        build_path = built_dir.joinpath(BUILD_TEMP_DIR_PATH).joinpath(Path.cwd().name)
        expected_root_file_path = build_path.joinpath(
            "platform/service/root/us-east-2/000/root_file.txt"
        )
        assert expected_root_file_path.exists()
        assert expected_root_file_path.is_file()
        assert expected_root_file_path.read_text() == "root file"
