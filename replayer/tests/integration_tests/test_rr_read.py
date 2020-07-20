import time
import cpager
from interruptingcow import timeout

from pager.consts import DUMP_DIRECTORY
from replayer.replayer import run_replayer_on_records_at_path


def test_read_from_file_happy_flow(run_python_script, recorder_context_manager, pager_listener_context_manager,
                                   dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path):
    file_name = "myfile.txt"
    script_name = "open_and_read.py"
    expected_output = b'Hi Son'
    with open(str(scripts_path / file_name), 'wb') as f:
        f.write(expected_output)

    with recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
        recorded_process = run_python_script(script_name, [expected_output])
        with timeout(seconds=1000):
            _, stderr = recorded_process.communicate()
        assert recorded_process.returncode == 0

    # write something else to file so we know we're getting old value on replay
    with open(str(scripts_path / file_name), 'w') as f:
        f.write("what")

    with timeout(seconds=1000):
        print('STARTING')
        print(recorded_process.pid)
        with replaying_context_manager():
            # replayed_process = run_python_script(script_name, [expected_output])
            cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
            exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
            # _, stderr = replayed_process.communicate()
        assert exit_code == 0
