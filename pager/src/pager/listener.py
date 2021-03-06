import os
import signal
from pathlib import Path

import cpager
from multiprocessing.connection import Listener as MultiProcessingListener
import time
from pager.consts import PORT, BASE_DIRECTORY
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

            directory = self.base_directory / str(pid)
            self.base_directory.mkdir(exist_ok=True)
            directory.mkdir(exist_ok=True)
            cpager.take_snapshot(pid, str(directory))
            start_recording(pid)
            os.kill(pid, signal.SIGCONT)


def run_listener():
    Listener.create().run()


if __name__ == '__main__':
    Listener.create().run()
