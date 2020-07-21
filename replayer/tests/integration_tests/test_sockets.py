import contextlib
import multiprocessing
import socket


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
