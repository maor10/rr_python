import multiprocessing
import os
import time

import cinterceptor
import pytest

CALLED = {
    'called': False
}


def runner():
    while True:
        os.path.exists('/does/not/matter')


def create_handler_for_process(process: multiprocessing.Process):
    def handler(*args):
        process.kill()
    return handler


@pytest.fixture
def run_replayed_process():

    process = multiprocessing.Process(target=runner)

    def _run():
        process.start()
        return process

    yield _run

    if process.is_alive():
        process.terminate()


def test_calls_syscall_handler_on_syscall(run_replayed_process, run_replayer_process):
    process = run_replayed_process()
    run_replayer_process(handler=create_handler_for_process(process), process_to_replay=process)
    # TODO - change this - we don't know what exactly we're waiting for (for example, which sys call will happen)
    #  so just sleep for a second, eventually a syscall will hit (python reading the program or os.path.exists)
    time.sleep(1)
    assert not process.is_alive()
