import contextlib
import multiprocessing
import time

from flask import Flask


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


def test_requests_happy_flow(assert_record_and_replay):
    with flask_app():
        assert_record_and_replay("request_from_localhost.py")


def test_https_requests_happy_flow(assert_record_and_replay):
    assert_record_and_replay("https_requests.py")


if __name__ == '__main__':
    with flask_app():
        time.sleep(1000)
