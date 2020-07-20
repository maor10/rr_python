from interruptingcow import timeout
import cpager
from pager.consts import DUMP_DIRECTORY
from replayer import run_replayer_on_records_at_path


def test_ssl_happy_flow(run_python_script, recorder_context_manager, dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path, pager_listener_context_manager):
    script_name = "ssl_test.py"

    #
    # import os
    # os.environ['OPENSSL_ia32cap'] = f'~{env_var}:~0'

    with recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
        recorded_process = run_python_script(script_name, [])
        with timeout(seconds=3):
            recorded_stdout, stderr = recorded_process.communicate()
            print(recorded_stdout)

    with timeout(seconds=1000):
        with replaying_context_manager():
            cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
            # replayed_process = run_python_script(script_name, [])
            exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
            # replayed_stdout, stderr = replayed_process.communicate()
        assert exit_code == 0
        # assert recorded_stdout == replayed_stdout