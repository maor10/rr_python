import contextlib
import multiprocessing
import os
import signal
import subprocess
import sys
import time

import cpyrecorder
import interruptingcow
import psutil
import pytest

from pyrecorder import record
import ctypes


@pytest.fixture
def run_python_script(scripts_path):
    processes = []

    def _run_script(script_name, arguments=None):
        arguments = arguments or []
        process = subprocess.Popen(["python3", str(scripts_path / script_name), *arguments],)
                                   # stdout=subprocess.PIPE,
                                   # stderr=subprocess.PIPE,
                                   # stdin=subprocess.PIPE)
        processes.append(process)
        return process

    yield _run_script

    for p in processes:
        if p.poll() is None:
            p.kill()


@pytest.fixture
def run_adder_process():
    process = None

    def _run():
        nonlocal process
        process = subprocess.Popen(["python3", os.path.join(os.path.abspath(os.path.dirname(__file__)), 'scripts', 'adder.py')])
        return process

    yield _run
    # if process is not None and process.poll():
    #     process.kill()


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

#
# def test_recording_happy_flow(adder_process):
#     adder_process.start()
#     process = psutil.Process(adder_process.pid)
#     with interruptingcow.timeout(2):
#         while process.is_running() and process.status() != 'zombie':
#             assert process.status() != 'stopped'
#


def test_replaying_raises_sigstop(replaying_context_manager, run_adder_process):
    with replaying_context_manager():
        process = run_adder_process()
        process = psutil.Process(process.pid)
        with interruptingcow.timeout(2):
            while process.is_running() and process.status() != 'stopped':
                assert process.status() != 'zombie'


class sigval_t(ctypes.Union):
    _fields_ = [
        ('sigval_int', ctypes.c_int),
        ('sigval_ptr', ctypes.c_void_p)
        ]


def test_replaying_continues_until_next_line(replaying_context_manager, run_adder_process):
    with replaying_context_manager():
        process = run_adder_process()
        process = psutil.Process(process.pid)
        with interruptingcow.timeout(2):
            while process.is_running() and process.status() != 'stopped':
                assert process.status() != 'zombie'

        libc = ctypes.cdll.LoadLibrary("libc.so.6")
        sigqueue = libc.sigqueue
        sigqueue.argtypes = [ctypes.c_int, ctypes.c_int, sigval_t]

        val = sigval_t()
        val.sigval_int = 10

        import ipdb; ipdb.set_trace()
        # sigqueue(process.pid, signal.SIGUSR1, val)
        # os.kill(process.pid, signal.SIGUSR1)
        print(process.status())
        os.kill(process.pid, signal.SIGCONT)
        print(process.status())
        time.sleep(1)
        print(process.status())
        assert 0
        # os.kill(process.pid, signal.SIGUSR1)
