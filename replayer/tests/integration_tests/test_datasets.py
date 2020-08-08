import pytest


def test_datasets(assert_record_and_replay, scripts_path):
    script_name = "insert_and_read_datasets.py"
    assert_record_and_replay(script_name)
