import os
import sys
from pyrecorder import record


@record
def play():
    path = sys.argv[1]
    expected_output = sys.argv[2]
    content = open(path, 'r').read()
    assert content == expected_output, f"File content was {content}, expected was {expected_output}"


play()
