import pytest

from launch.lib.automation.common.functions import single_true


def test_single_true():
    assert single_true([True, False, False]) == True
    assert single_true([False, True, False]) == True
    assert single_true([False, False, True]) == True
    assert single_true([True, True, False]) == False
    assert single_true([True, False, True]) == False
    assert single_true([False, True, True]) == False
    assert single_true([True, True, True]) == False
    assert single_true([False, False, False]) == False
    assert single_true([]) == False
