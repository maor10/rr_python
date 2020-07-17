import sys
sys.path.append('/projects/stuffs/rr_python/pyrecorder/src')
import cpyrecorder
import os
import signal


def f(a):
    cpyrecorder.record_or_replay()
    while a:
        print(1)
        break
    else:
        print(2)


f(True)
