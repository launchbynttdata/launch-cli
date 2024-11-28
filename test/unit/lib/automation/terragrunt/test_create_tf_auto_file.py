from unittest import mock

import click
import pytest

from launch.lib.automation.terragrunt.functions import create_tf_auto_file


def test_create_tf_auto_file_dry_run(mocker, fakedata):
    data = fakedata["create_tf_auto_file"]["data"]
    out_file = fakedata["create_tf_auto_file"]["out_file"]
    dry_run = True

    mock_secho = mocker.patch("click.secho")

    create_tf_auto_file(data, out_file, dry_run)

    mock_secho.assert_called_once_with(
        f"[DRYRUN] Would have written to file: {out_file=}, {data=}", fg="yellow"
    )


def test_create_tf_auto_file_write(mocker, fakedata):
    data = fakedata["create_tf_auto_file"]["data"]
    out_file = fakedata["create_tf_auto_file"]["out_file"]
    dry_run = False

    mock_open = mocker.patch("builtins.open", mock.mock_open())
    mock_secho = mocker.patch("click.secho")

    create_tf_auto_file(data, out_file, dry_run)

    mock_open.assert_called_once_with(out_file, "w")
    mock_open().write.assert_any_call("key1 = value1\n")
    mock_open().write.assert_any_call("key2 = value2\n")
    mock_secho.assert_called_once_with(f"Wrote to file: {out_file=}", fg="green")
