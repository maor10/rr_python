import contextlib
import multiprocessing
import os
import signal
import sys
import time

import cpyrecorder
import interruptingcow
import psutil
import pytest

from pyrecorder import record


@record
def adder(a, b):
    c = a + b
    return c


@pytest.fixture
def adder_process():
    process = multiprocessing.Process(target=adder, args=(2, 2))
    yield process
    if process.is_alive():
        process.kill()


@pytest.fixture
def replaying_context_manager():
    @contextlib.contextmanager
    def replayer():
        with open(str(cpyrecorder.REPLAY_ENVIRONMENT_FILE_PATH), 'wb') as f:
            f.write(b'1')
        try:
            yield
        finally:
            if os.path.exists(cpyrecorder.REPLAY_ENVIRONMENT_FILE_PATH):
                os.remove(cpyrecorder.REPLAY_ENVIRONMENT_FILE_PATH)
    return replayer


def test_recording_happy_flow(adder_process):
    adder_process.start()
    process = psutil.Process(adder_process.pid)
    with interruptingcow.timeout(2):
        while process.is_running() and process.status() != 'zombie':
            assert process.status() != 'stopped'


def test_replaying_raises_sigstop(replaying_context_manager, adder_process):
    with replaying_context_manager():
        adder_process.start()
        process = psutil.Process(adder_process.pid)
        with interruptingcow.timeout(2):
            while process.is_running() and process.status() != 'stopped':
                assert process.status() != 'zombie'


# def test_replaying_continues_until_next_line(replaying_context_manager, adder_process):
#     with replaying_context_manager():
#         adder_process.start()
#         process = psutil.Process(adder_process.pid)
#         with interruptingcow.timeout(2):
#             while process.is_running() and process.status() != 'stopped':
#                 assert process.status() != 'zombie'
#         os.kill(process.pid, signal.SIGUSR1, )
#         os.kill(process.pid, signal.SIGCONT)
#
#
