import os
import signal
from functools import wraps
from pyrecorder import consts
from pyrecorder.km_communicator import start_recording
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
        # if not consts.REPLAY_SERVER_PROC_PATH.exists():
        #     start_recording()
        return func(*args, **kwargs)
    return _wrapper
