import contextlib
import multiprocessing
import time

from interruptingcow import timeout
from flask import Flask

from pager.consts import DUMP_DIRECTORY
from replayer.replayer import run_replayer_on_records_at_path
import cpager


def run_flask_app():
    app = Flask(__name__)

    @app.route('/ping')
    def pong():
        return 'pong'

    app.run('0.0.0.0', 8000)


@contextlib.contextmanager
def flask_app():
    process = multiprocessing.Process(target=run_flask_app)
    process.start()
    try:
        yield
    finally:
        if process.is_alive():
            process.terminate()


def test_requests_happy_flow(run_python_script, recorder_context_manager, dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path, pager_listener_context_manager):
    script_name = "make_requests.py"

    with flask_app(), recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
        recorded_process = run_python_script(script_name, [])
        with timeout(seconds=3):
            _, stderr = recorded_process.communicate()
        assert recorded_process.returncode == 0

    with timeout(seconds=1000):
        with replaying_context_manager():
            # replayed_process = run_python_script(script_name, [])
            cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
            exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
        assert exit_code == 0, stderr


def test_https_requests_happy_flow(run_python_script, recorder_context_manager, dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path, pager_listener_context_manager):
    script_name = "https_requests.py"

    import os
    import os
    # os.environ['OPENSSL_ia32cap'] = '~4611686018427387920:~0'
    # os.environ['OPENSSL_ia32cap'] = '~4611686018427387904:~0'

    with recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
        recorded_process = run_python_script(script_name, [])
        with timeout(seconds=3):
            recorded_stdout, stderr = recorded_process.communicate()

    with timeout(seconds=1000):
        with replaying_context_manager():
            cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
            time.sleep(1)
            # replayed_process = run_python_script(script_name, [])
            exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
            # replayed_stdout, stderr = replayed_process.communicate()
        assert exit_code == 0
        # assert recorded_stdout == replayed_stdout


if __name__ == '__main__':
    with flask_app():
        time.sleep(1000)