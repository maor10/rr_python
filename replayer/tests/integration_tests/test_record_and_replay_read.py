import time

from interruptingcow import timeout

from replayer.replayer import run_replayer_on_records_at_path


def test_run_records(run_python_script, recorder_context_manager, dumper_context_manager,
                     scripts_path, replaying_context_manager, records_path):
    file_name = "myfile.txt"
    expected_output = b'Hi Son'
    with open(str(scripts_path / file_name), 'wb') as f:
        f.write(expected_output)

    with recorder_context_manager(), dumper_context_manager():
        recorded_process = run_python_script("read_from_input.py")
        with timeout(seconds=3):
            stdout, stderr = recorded_process.communicate()
        assert stdout.strip() == expected_output.strip(), "Original run did not output as expected"
        recorded_process.kill()

    # write something else to file so we know we're getting old value on replay
    with open(str(scripts_path / file_name), 'w') as f:
        f.write("what")

    with timeout(seconds=3):
        with replaying_context_manager():
            replayed_process = run_python_script("read_from_input.py")
            run_replayer_on_records_at_path(replayed_process.pid, records_path)
            stdout, stderr = replayed_process.communicate()

    time.sleep(1)

    assert stdout.strip() == expected_output.strip()
