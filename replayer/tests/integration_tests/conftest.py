import contextlib
import multiprocessing
import os
import subprocess
import time
from pathlib import Path
import cpager
import pytest
from interruptingcow import timeout

import pager
from pager import run_listener
from pyrecorder import REPLAY_SERVER_PROC_PATH
from replayer import run_replayer_on_records_at_path

DUMP_PATH = '/proc/syscall_dumper'

# TODO: is there a better way to do this?? Maybe in install set env var..


@pytest.fixture
def kernel_module_directory():
    directory = Path(__file__).parent
    while directory.stem != "rr_python":
        directory = directory.parent
        if str(directory) == '/':
            raise Exception("Could not find base project directory")
    return directory / 'recorder' / 'src'


@pytest.fixture(autouse=True)
def raise_if_not_root():
    if os.getuid() != 0:
        raise Exception("You must be root to run integration tests (for criu to work)")


@pytest.fixture
def records_path():
    return Path('/tmp/records.dump')


@pytest.fixture
def scripts_path():
    return Path(__file__).parent / "scripts"


@pytest.fixture
def run_python_script(scripts_path):
    processes = []

    def _run_script(script_name, arguments=None):
        arguments = arguments or []
        process = subprocess.Popen(["python3", str(scripts_path / script_name), *arguments],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
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
def recorder_context_manager(kernel_module_directory):
    @contextlib.contextmanager
    def recorder():
        if REPLAY_SERVER_PROC_PATH.exists():
            REPLAY_SERVER_PROC_PATH.unlink()
        subprocess.check_output([f"insmod", f"{kernel_module_directory}/record.ko"],
                                stderr=subprocess.STDOUT)
        try:
            yield
        finally:
            subprocess.check_output([f"rmmod", "record"],
                                    stderr=subprocess.STDOUT)
    return recorder


@pytest.fixture
def pager_listener_context_manager():
    @contextlib.contextmanager
    def listener():
        process = multiprocessing.Process(target=run_listener)
        process.start()
        try:
            yield
        finally:
            if process.is_alive():
                process.kill()
    return listener


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


@pytest.fixture
def assert_record_and_replay(run_python_script, recorder_context_manager, dumper_context_manager,
                             replaying_context_manager,
                             pager_listener_context_manager, scripts_path, records_path):
    replayed_stdout = b''

    def stdout_callback(text):
        nonlocal replayed_stdout
        replayed_stdout += text

    def _run(script_name, runtime_arguments=None, print_stdouts=False):
        with recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
            recorded_process = run_python_script(script_name, runtime_arguments or [])
            with timeout(seconds=3):
                recorded_stdout, stderr = recorded_process.communicate()
            assert recorded_process.returncode == 0, f"Recorded process returned a non-zero exit code\nstderr: {stderr}"

        with replaying_context_manager():
            with timeout(seconds=10000):
                cpager.restore_from_snapshot(str(pager.BASE_DIRECTORY / str(recorded_process.pid)))
                exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path,
                                                            stdout_callback=stdout_callback)

        if print_stdouts:
            print(f"Recorded STDOUT: {recorded_stdout}")
            print(f"Replayed STDOUT: {replayed_stdout}")
        assert exit_code == 0, stderr
        assert recorded_stdout == replayed_stdout

    return _run
