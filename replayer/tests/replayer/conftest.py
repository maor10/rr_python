import os
import subprocess
import time
from pathlib import Path
import replayer
import pytest

from replayer.replayer import Replayer, run_replayer
from replayer.system_call_runners import SystemCallRunner


def get_output_path_for_binary_with_name(name):
    return Path(f'/tmp/{name}.out')


@pytest.fixture
def compile_binary():
    binary_name = None

    def _compile_binary(name):
        nonlocal binary_name
        binary_name = name
        test_binary_directory = Path(replayer.__file__).parent.parent.parent / 'tests' / 'test_binary'
        os.system(f"gcc -o {get_output_path_for_binary_with_name(binary_name)} {test_binary_directory}/{binary_name}.c")
        os.system(f"chmod 777 {get_output_path_for_binary_with_name(binary_name)}")
    yield _compile_binary

    if binary_name:
        output_path = get_output_path_for_binary_with_name(binary_name)
        if output_path.exists():
            output_path.unlink()

    return _compile_binary


@pytest.fixture
def run_test_binary(compile_binary):
    process = None

    def _run_popen(binary_name, args):
        nonlocal process
        compile_binary(binary_name)
        process = subprocess.Popen([str(get_output_path_for_binary_with_name(binary_name)), *args],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    yield _run_popen
    if process.poll() is None:
        process.terminate()


@pytest.fixture
def run_system_calls_on_binary(run_test_binary):

    previous_system_call_numbers_to_runners = {}

    def _run(binary_name, arguments_for_binary, system_call_numbers_to_handle, system_calls):
        nonlocal previous_system_call_numbers_to_runners
        child = run_test_binary(binary_name, arguments_for_binary)
        time.sleep(0.5)
        previous_system_call_numbers_to_runners = SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS
        new_system_call_numbers_to_runners = {
            sys_call_number: runner
            for sys_call_number, runner in SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS.items()
            if sys_call_number in system_call_numbers_to_handle
        }
        SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS = new_system_call_numbers_to_runners
        run_replayer(child.pid, system_calls=system_calls)

        out, err = child.communicate()
        assert not err, f"Failed, binary output: {err.decode('utf-8')}"

    yield _run

    SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS = previous_system_call_numbers_to_runners