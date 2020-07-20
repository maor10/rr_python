import os
import subprocess
import time
from pathlib import Path
import replayer
import pytest

from replayer import run_replayer
from replayer.system_call_runners import SystemCallRunner


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
        exit_code = run_replayer(child.pid, system_calls=system_calls)
        _, err = child.communicate()
        assert exit_code == 0, err

    yield _run

    SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS = previous_system_call_numbers_to_runners
