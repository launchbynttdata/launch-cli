import pytest

from launch.lib.service.template.functions import get_value_by_path
from test.conftest import fakeData_forLibServiceTemplateFunction as fakeData

def test_get_value_by_path_success(fakeData):
    path = 'a/b/c'
    result = get_value_by_path(fetch_fake_data(fakeData), path)
    assert result == 'value'

def test_get_value_by_path_failure(fakeData):
    path = 'a.b.d'
    result = get_value_by_path(fetch_fake_data(fakeData), path)
    assert result is None

def test_get_value_by_path_empty_path(fakeData):
    path = ''
    result = get_value_by_path(fetch_fake_data(fakeData), path)
    assert result is None

def test_get_value_by_path_nonexistent_key(fakeData):
    path = 'a/1/c'
    result = get_value_by_path(fetch_fake_data(fakeData), path)
    assert result is None

def fetch_fake_data(fakeData):
    return fakeData("fakeData_forGetValueByPath.json")