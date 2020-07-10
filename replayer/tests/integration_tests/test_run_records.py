import contextlib
import multiprocessing
import os
import subprocess
import time
from pathlib import Path

import pytest
from interruptingcow import timeout


# TODO Test fails on Operation not Permitted on attach, fix
from pyrecorder import REPLAY_SERVER_PROC_PATH
from replayer.replayer import Replayer, run_replayer_on_records_at_path

SCRIPTS_PATH = Path(__file__).parent / "scripts"
RECORDS_PATH = Path('/tmp/records.dump')
DUMP_PATH = '/proc/syscall_dumper'

KERNEL_MODULE_DIRECTORY = "/projects/stuffs/rr_python/recorder/src"


@pytest.fixture
def run_python_script():
    processes = []

    def _run_script(script_name):
        process = subprocess.Popen(["python3", str(SCRIPTS_PATH / script_name)]
                                   , stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        processes.append(process)
        return process

    yield _run_script

    for p in processes:
        if p.poll() is None:
            p.kill()


@contextlib.contextmanager
def dumper():
    process = subprocess.Popen(["dd", "if=/proc/syscall_dumper", "bs=30M", f"of={str(RECORDS_PATH)}"])
    yield
    print("killing dumper")
    if process.poll() is None:
        process.kill()


@contextlib.contextmanager
def recorder():
    os.system(f"sudo insmod {KERNEL_MODULE_DIRECTORY}/record.ko")
    yield
    print("removving recordmod")
    os.system(f"sudo rmmod record")


@pytest.fixture
def clean_records_path():
    if RECORDS_PATH.exists():
        RECORDS_PATH.unlink()


def test_run_records(clean_records_path, run_python_script):
    if REPLAY_SERVER_PROC_PATH.exists():
        REPLAY_SERVER_PROC_PATH.unlink()

    with recorder(), dumper():
        expected_output = b'Hi Son'
        with open(str(SCRIPTS_PATH / 'myfile.txt'), 'wb') as f:
            f.write(expected_output)

        recorded_process = run_python_script("read_from_input.py")
        with timeout(seconds=15):
            stdout, stderr = recorded_process.communicate()
        assert stdout.strip() == expected_output.strip(), "Original run did not output as expected"
        recorded_process.kill()

        # let dumper finish...
        time.sleep(1)

    with open(str(SCRIPTS_PATH / 'myfile.txt'), 'w') as f:
        f.write("what")

    with open(str(REPLAY_SERVER_PROC_PATH), 'wb') as f:
        f.write(b'1')

    replayed_process = run_python_script("read_from_input.py")
    run_replayer_on_records_at_path(replayed_process.pid, RECORDS_PATH)

    with timeout(seconds=3):
        print("Let's go...")
        stdout, stderr = replayed_process.communicate()

    time.sleep(1)

    assert stdout.strip() == expected_output.strip()

