import os
import signal
from pathlib import Path

import cpager
from multiprocessing.connection import Listener as MultiProcessingListener
import time
from pager.consts import PORT, BASE_DIRECTORY, DUMP_DIRECTORY
from pager.km_communicator import start_recording


class Listener:
    """
    Responsible for listening to incoming requests to take snapshots of processes
    """

    def __init__(self, listener: MultiProcessingListener, base_directory: Path):
        self.listener = listener
        self.base_directory = base_directory

    @classmethod
    def create(cls):
        return cls(MultiProcessingListener(('0.0.0.0', PORT)), BASE_DIRECTORY)

    def run(self):
        """
        Runs the listener in a forever loop waiting and processing incoming snapshot requests
        :return:
        """
        while True:
            conn = self.listener.accept()
            pid = conn.recv()

            # directory = self.base_directory / DUMP_DIRECTORY_NAME  #  str(pid)
            DUMP_DIRECTORY.mkdir(exist_ok=True)
            start = time.time()
            cpager.take_snapshot(pid, str(DUMP_DIRECTORY))
            end = time.time()
            print(end - start)
            start_recording(pid)
            os.kill(pid, signal.SIGCONT)


def run_listener():
    Listener.create().run()


if __name__ == '__main__':
    Listener.create().run()
