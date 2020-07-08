import os
import signal
from functools import wraps
import ipdb
from pyrecorder import consts


def record(func):
    """
    TODO: Make this actually work
    """
    @wraps(func)
    def _wrapper(*args, **kwargs):
        if consts.REPLAY_SERVER_SPECIAL_PATH.exists():
            os.kill(os.getpid(), signal.SIGSTOP)
            ipdb.set_trace()
        return func(*args, **kwargs)
    return _wrapper
