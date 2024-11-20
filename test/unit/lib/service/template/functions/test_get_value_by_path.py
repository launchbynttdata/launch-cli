import pytest

from launch.lib.service.template.functions import get_value_by_path
from test.conftest import fakeData_forPath

def test_get_value_by_path_success(fakeData_forPath):
    path = 'a/b/c'
    result = get_value_by_path(fakeData_forPath, path)
    assert result == 'value'

def test_get_value_by_path_failure(fakeData_forPath):
    path = 'a.b.d'
    result = get_value_by_path(fakeData_forPath, path)
    assert result is None

def test_get_value_by_path_empty_path(fakeData_forPath):
    path = ''
    result = get_value_by_path(fakeData_forPath, path)
    assert result is None

def test_get_value_by_path_nonexistent_key(fakeData_forPath):
    path = 'a/1/c'
    result = get_value_by_path(fakeData_forPath, path)
    assert result is None
