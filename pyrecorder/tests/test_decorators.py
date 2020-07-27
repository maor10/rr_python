import multiprocessing
import os
from pathlib import Path
import psutil
import pytest
from interruptingcow import timeout

from pyrecorder import record


@pytest.fixture
def run_replayer():

    process = None

    def _run_replayer(with_replay_environment_file=False):
        nonlocal process

        def _run_in_subprocess():
            Path.exists = lambda *s, **k: with_replay_environment_file

            print(with_replay_environment_file)

            @record
            def run():
                pass

            return run()

        process = multiprocessing.Process(target=_run_in_subprocess)
        process.start()

        return process

    yield _run_replayer

    if process is not None and process.is_alive():
        process.kill()


def test_record_when_replaying(run_replayer, pager_listener_context_manager):
    with pager_listener_context_manager():
        multiprocessing_process = run_replayer(with_replay_environment_file=True)
        process = psutil.Process(pid=multiprocessing_process.pid)
        with timeout(seconds=2):
            while process.status() == "running":
                pass
            assert process.status() == "stopped"


# def test_record_when_not_replaying(run_replayer, pager_listener_context_manager):
#     with pager_listener_context_manager():
#         multiprocessing_process = run_replayer(with_replay_environment_file=False)
#         process = psutil.Process(pid=multiprocessing_process.pid)
#         with timeout(seconds=2):
#             while process.status() == "running":
#                 pass
#             assert process.status() == "zombie"
