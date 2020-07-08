import subprocess

from replayer import run_replayer, run_replayer_on_records_at_path

# TODO Test fails on Operation not Permitted on attach, fix


def test_run_records():
    expected_stdout = 'Hi Tania'
    process = subprocess.Popen(["python3", "-c", f"os.kill(os.getpid(), signal.SIGSTOP); print('{expected_stdout}')"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_replayer_on_records_at_path(process.pid, './records/record')
    out, err = process.communicate()
    assert out == expected_stdout
