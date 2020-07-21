import contextlib
import multiprocessing
import socket
from interruptingcow import timeout
from pytest import fixture

from pager.consts import DUMP_DIRECTORY
from replayer import run_replayer_on_records_at_path
import cpager


HOST = 'localhost'
PORT = 8001


def run_socket_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Waiting for con', addr)
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)


@contextlib.contextmanager
def socket_listener():
    process = multiprocessing.Process(target=run_socket_listener)
    process.start()
    try:
        yield
    finally:
        if process.is_alive():
            process.terminate()


def test_sockets_record_and_replay_happy_flow(assert_record_and_replay):
    script_name = "sockets.py"
    arguments = [HOST, str(PORT)]
    with socket_listener():
        assert_record_and_replay(script_name, arguments)

# def test_sockets_record_and_replay_happy_flow(run_python_script, recorder_context_manager, dumper_context_manager,
#                      scripts_path, replaying_context_manager, records_path, pager_listener_context_manager):
#     expected_output = b'Hi Son'
#     script_name = "sockets.py"
#     arguments = [HOST, str(PORT), expected_output]
#     with socket_listener(), recorder_context_manager(), dumper_context_manager(), pager_listener_context_manager():
#         recorded_process = run_python_script(script_name, arguments)
#         with timeout(seconds=3):
#             _, stderr = recorded_process.communicate()
#         assert recorded_process.returncode == 0
#
#     with replaying_context_manager():
#         with timeout(seconds=30000):
#             # replayed_process = run_python_script(script_name, arguments)
#             cpager.restore_from_snapshot(str(DUMP_DIRECTORY))
#             exit_code = run_replayer_on_records_at_path(recorded_process.pid, records_path)
#             # _, stderr = replayed_process.communicate()
#     assert exit_code == 0, stderr
