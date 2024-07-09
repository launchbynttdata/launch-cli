import pytest

from launch.lib.common.utilities import recursive_dictionary_merge


def test_merge_shallow():
    a = {"key1": "value1"}
    b = {"key2": "value2"}

    result = recursive_dictionary_merge(a=a, b=b)
    assert result == {"key1": "value1", "key2": "value2"}


def test_merge_deep():
    a = {"foo": {"bar": {"baz": "value1"}}}
    b = {"foo": {"bar": {"quux": "value2"}}}

    result = recursive_dictionary_merge(a=a, b=b)
    assert result == {"foo": {"bar": {"baz": "value1", "quux": "value2"}}}


def test_merge_conflict_shallow():
    a = {"key1": "value1"}
    b = {"key1": "value2"}

    with pytest.raises(ValueError, match="Conflict at key1"):
        result = recursive_dictionary_merge(a=a, b=b)


def test_merge_conflict_deep():
    a = {"foo": {"bar": {"baz": "value1"}}}
    b = {"foo": {"bar": {"baz": "value2"}}}

    with pytest.raises(ValueError, match="Conflict at foo.bar.baz"):
        result = recursive_dictionary_merge(a=a, b=b)
