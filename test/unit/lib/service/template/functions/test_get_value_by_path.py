import pytest

from unittest import mock
from launch.lib.service.template.functions import get_value_by_path

def test_get_value_by_path_success():
    data = {
        'a': {
            'b': {
                'c': 'value'
            }
        }
    }
    path = 'a/b/c'
    result = get_value_by_path(data, path)
    assert result == 'value'

def test_get_value_by_path_failure():
    data = {
        'a': {
            'b': {
                'c': 'value'
            }
        }
    }
    path = 'a.b.d'
    result = get_value_by_path(data, path)
    assert result is None

def test_get_value_by_path_empty_path():
    data = {
        'a': {
            'b': {
                'c': 'value'
            }
        }
    }
    path = ''
    result = get_value_by_path(data, path)
    assert result is None

def test_get_value_by_path_nonexistent_key():
    data = {
        'a': {
            'b': {
                'c': 'value'
            }
        }
    }
    path = 'a.x.c'
    result = get_value_by_path(data, path)
    assert result is None
