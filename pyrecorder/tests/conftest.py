import contextlib
import multiprocessing
import os
import signal

import pytest

import pager
from pager import run_listener


@pytest.fixture(autouse=True)
def patch_pager(monkeypatch):
    monkeypatch.setattr(pager, 'send_request_to_take_snapshot', lambda *_: os.kill(os.getpid(), signal.SIGSTOP))
