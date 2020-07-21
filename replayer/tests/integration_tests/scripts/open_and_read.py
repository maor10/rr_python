import os
import sys
from pyrecorder import record


@record
def play():
    print("hello!")
    a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myfile.txt'), 'r').read()
    assert a == sys.argv[1]


play()
