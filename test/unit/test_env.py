from contextlib import ExitStack as does_not_raise
from random import randint

import pytest

from launch import env


@pytest.mark.parametrize(
    "input_value, expected_return, raises",
    [
        ("y", True, does_not_raise()),
        ("Y", True, does_not_raise()),
        ("yes", True, does_not_raise()),
        ("t", True, does_not_raise()),
        ("True", True, does_not_raise()),
        ("ON", True, does_not_raise()),
        ("1", True, does_not_raise()),
        ("n", False, does_not_raise()),
        ("N", False, does_not_raise()),
        ("no", False, does_not_raise()),
        ("f", False, does_not_raise()),
        ("False", False, does_not_raise()),
        ("ofF", False, does_not_raise()),
        ("0", False, does_not_raise()),
        ("yep", None, pytest.raises(ValueError)),
        ("yeah", None, pytest.raises(ValueError)),
        ("nope", None, pytest.raises(ValueError)),
        ("219", None, pytest.raises(ValueError)),
        ("$", None, pytest.raises(ValueError)),
    ],
)
def test_strtobool(input_value, expected_return, raises):
    with raises:
        assert env.strtobool(input_value) == expected_return


@pytest.mark.parametrize(
    "variable_name, variable_value, expected_value",
    [("LAUNCH_EXAMPLE_TRUE", "1", True), ("LAUNCH_EXAMPLE_FALSE", "0", False)],
)
def test_get_bool_env_var(variable_name, variable_value, expected_value, mocker):
    mocker.patch.object(env.os.environ, "get", return_value=variable_value)
    assert (
        env.get_bool_env_var(variable_name, default_value=not expected_value)
        == expected_value
    )


def test_get_bool_env_var_not_exists():
    """Mocking out an env var that doesn't exist is a pain, so we'll just choose a random number between a million and a billion and hope nobody has set that var on their system."""
    assert (
        env.get_bool_env_var(str(randint(1000000, 1000000000)), default_value=True)
        == True
    )
