import contextlib
import os
import subprocess
import time
from pathlib import Path

import pytest

from pyrecorder import REPLAY_SERVER_PROC_PATH
from replayer import run_replayer_on_records_at_path

DUMP_PATH = '/proc/syscall_dumper'

KERNEL_MODULE_DIRECTORY = "/projects/stuffs/rr_python/recorder/src"


@pytest.fixture
def records_path():
    return Path('/tmp/records.dump')


@pytest.fixture
def scripts_path():
    return Path(__file__).parent / "scripts"


@pytest.fixture
def run_python_script(scripts_path):
    processes = []

    def _run_script(script_name):
        process = subprocess.Popen(["python3", str(scripts_path / script_name)]
                                   , stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        processes.append(process)
        return process

    yield _run_script

    for p in processes:
        if p.poll() is None:
            p.kill()


@pytest.fixture
def dumper_context_manager(records_path):
    @contextlib.contextmanager
    def dumper():
        process = subprocess.Popen(["dd", "if=/proc/syscall_dumper", "bs=30M", f"of={str(records_path)}"])
        try:
            yield
        finally:
            # let dumper finish...
            time.sleep(0.3)
            print("killing dumper")
            if process.poll() is None:
                process.kill()
    return dumper


@pytest.fixture
def recorder_context_manager():
    @contextlib.contextmanager
    def recorder():
        if REPLAY_SERVER_PROC_PATH.exists():
            REPLAY_SERVER_PROC_PATH.unlink()
        os.system(f"sudo insmod {KERNEL_MODULE_DIRECTORY}/record.ko")
        try:
            yield
        finally:
            print("removing recordmod")
            os.system(f"sudo rmmod record")
    return recorder


@pytest.fixture
def replaying_context_manager():
    @contextlib.contextmanager
    def replayer():
        with open(str(REPLAY_SERVER_PROC_PATH), 'wb') as f:
            f.write(b'1')
        try:
            yield
        finally:
            if REPLAY_SERVER_PROC_PATH.exists():
                REPLAY_SERVER_PROC_PATH.unlink()
    return replayer

