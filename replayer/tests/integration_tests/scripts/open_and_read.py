import os

from pyrecorder import record


@record
def play():
    a = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'myfile.txt'), 'r').read()
    print(a)


play()
