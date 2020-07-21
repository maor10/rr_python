import time
from pathlib import Path

from interruptingcow import timeout
import cpager
import pager
from pager import Client
from pager.consts import DUMP_DIRECTORY
from replayer import run_replayer_on_records_at_path


def test_binary_random_happy_flow(run_test_binary, run_python_script, recorder_context_manager, dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path, pager_listener_context_manager):

    # os.environ['OPENSSL_ia32cap'] = '~4611686018427387920:~0'
    # os.environ['OPENSSL_ia32cap'] = '~4611686018427387904:~0'
    with recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
        recorded_process = run_test_binary(directory=str(Path(__file__).parent / 'test_binary'),
                                           binary_name='gen_random',
                                           compile_args=['-I//home/osboxes/openssl/include/openssl',
                                                         '-L/home/osboxes/openssl/lib -lcrypto'])
        with timeout(seconds=3):
            time.sleep(1)
            Client.create(pid=recorded_process.pid).connection.send(recorded_process.pid)
            recorded_stdout, stderr = recorded_process.communicate()

    with timeout(seconds=1000):
        with replaying_context_manager():
            cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
            # replayed_process = run_python_script(script_name, [])
            exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
            # replayed_stdout, stderr = replayed_process.communicate()
        assert exit_code == 0
        # assert recorded_stdout == replayed_stdout

