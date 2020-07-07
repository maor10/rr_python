import multiprocessing
import cinterceptor
import pytest


@pytest.fixture
def run_replayer_process():
    process = None

    def _run_replay(handler, process_to_replay):
        cinterceptor.start_replay_with_pid_and_handler(process_to_replay.pid, handler)

    def _run(handler, process_to_replay):
        nonlocal process
        process = multiprocessing.Process(target=_run_replay, args=(handler, process_to_replay))
        process.start()

    yield _run

    if process is not None and process.is_alive():
        process.terminate()
