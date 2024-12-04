import os
from pathlib import Path
from unittest import mock
import pytest
import click
from launch.lib.automation.terragrunt.functions import process_app_templates
from launch.config.common import NON_SECRET_J2_TEMPLATE_NAME, SECRET_J2_TEMPLATE_NAME
from launch.cli.j2.render import render

@pytest.fixture
def mock_context():
    return mock.Mock(spec=click.Context)

@pytest.fixture
def mock_path(tmp_path):
    return tmp_path

@pytest.fixture
def mock_template_dir(tmp_path):
    return tmp_path / "templates"

@pytest.fixture
def mock_aws_profile():
    return "default"

@pytest.fixture
def mock_aws_region():
    return "us-west-2"

@pytest.fixture
def mock_dry_run():
    return True

@pytest.fixture
def setup_files(mock_path, mock_template_dir):
    properties_path = mock_path / "properties"
    properties_path.mkdir(parents=True, exist_ok=True)
    (properties_path / "app1.properties").write_text("key1=value1\nkey2=value2")

    secret_template_dir = mock_template_dir / "app1"
    secret_template_dir.mkdir(parents=True, exist_ok=True)
    (secret_template_dir / SECRET_J2_TEMPLATE_NAME).write_text("secret template content")

    non_secret_template_dir = mock_template_dir / "app1"
    non_secret_template_dir.mkdir(parents=True, exist_ok=True)
    (non_secret_template_dir / NON_SECRET_J2_TEMPLATE_NAME).write_text("non-secret template content")

    return properties_path

def test_process_app_templates(mock_context, mock_path, mock_template_dir, mock_aws_profile, mock_aws_region, mock_dry_run, setup_files):
    properties_path = setup_files

    with mock.patch("os.listdir", return_value=["app1.properties"]), \
         mock.patch("pathlib.Path.exists", return_value=True), \
         mock.patch("launch.cli.j2.render.render") as mock_render:

        process_app_templates(
            context=mock_context,
            instance_path=mock_path,
            properties_path=properties_path,
            template_dir=mock_template_dir,
            aws_profile=mock_aws_profile,
            aws_region=mock_aws_region,
            dry_run=mock_dry_run,
        )

        mock_context.invoke.assert_any_call(render, values=properties_path / "app1.properties",
                                               template=mock_template_dir / "app1" / SECRET_J2_TEMPLATE_NAME,
                                               out_file=f"{mock_path}/app1.secret.auto.tfvars",
                                               type="secret",
                                               aws_secrets_profile=mock_aws_profile,
                                               aws_secrets_region=mock_aws_region,
                                               dry_run=mock_dry_run)

        mock_context.invoke.assert_any_call(render, values=properties_path / "app1.properties",
                                        template=mock_template_dir / "app1" / NON_SECRET_J2_TEMPLATE_NAME,
                                        out_file=f"{mock_path}/app1.non-secret.auto.tfvars",
                                        aws_secrets_profile=mock_aws_profile,
                                        aws_secrets_region=mock_aws_region,
                                        dry_run=mock_dry_run)

def test_process_app_templates_no_properties(mock_context, mock_path, mock_template_dir, mock_aws_profile, mock_aws_region, mock_dry_run):
    with mock.patch("os.listdir", return_value=[]), \
         mock.patch("pathlib.Path.exists", return_value=True), \
         mock.patch("launch.cli.j2.render.render") as mock_render:

        process_app_templates(
            context=mock_context,
            instance_path=mock_path,
            properties_path=mock_path / "properties",
            template_dir=mock_template_dir,
            aws_profile=mock_aws_profile,
            aws_region=mock_aws_region,
            dry_run=mock_dry_run,
        )

        mock_render.assert_not_called()

def test_process_app_templates_no_templates(mock_context, mock_path, mock_aws_profile, mock_aws_region, mock_dry_run, setup_files):
    properties_path = setup_files

    with mock.patch("os.listdir", return_value=["app1.properties"]), \
         mock.patch("pathlib.Path.exists", return_value=False), \
         mock.patch("launch.cli.j2.render.render") as mock_render:

        process_app_templates(
            context=mock_context,
            instance_path=mock_path,
            properties_path=properties_path,
            template_dir=mock_path / "non_existent_templates",
            aws_profile=mock_aws_profile,
            aws_region=mock_aws_region,
            dry_run=mock_dry_run,
        )

        mock_render.assert_not_called()