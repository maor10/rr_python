from contextlib import contextmanager
from pathlib import Path

import pytest


@contextmanager
def file_with_text(path, text):
    with open(str(path), 'wb') as f:
        f.write(text)
    yield
    if path.exists():
        path.unlink()


def test_read_from_file_happy_flow(assert_record_and_replay, scripts_path):
    expected_output = b"Hello boy"
    path = Path('/tmp/idowhatiwant.txt')
    with file_with_text(path, expected_output):
        script_name = "open_and_read.py"
        assert_record_and_replay(script_name, runtime_arguments=[path, expected_output])
