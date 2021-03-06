import os
import signal
from functools import wraps
from pyrecorder import consts
import cpyrecorder
import pager


def record(func):
    """
    TODO: Make this actually work
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        pager.send_request_to_take_snapshot()
        cpyrecorder.record_or_replay()
        return func(*args, **kwargs)
    return _wrapper
