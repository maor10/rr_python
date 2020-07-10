import os
import signal
from functools import wraps
from pyrecorder import consts
from pyrecorder.km_communicator import start_recording


def record(func):
    """
    TODO: Make this actually work
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        if consts.REPLAY_SERVER_PROC_PATH.exists():
            # import ipdb
            os.kill(os.getpid(), signal.SIGSTOP)
            # ipdb.set_trace()
        else:
            start_recording()
        return func(*args, **kwargs)
    return _wrapper
