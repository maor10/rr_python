import os
import signal
from multiprocessing.connection import Client as MultiProcessingClient
import time
from pager.consts import PORT


class Client:
    """
    Client to send requests to listener to take snapshots
    """
    def __init__(self, connection: MultiProcessingClient, pid: int):
        self.connection = connection
        self.pid = pid

    @classmethod
    def create(cls, pid=None):
        return cls(MultiProcessingClient(('localhost', PORT)), pid=pid or os.getpid())

    def send_request_to_take_snapshot(self):
        """
        Send a request to the listener to take a snapshot
        :return:
        """
        self.connection.send(self.pid)
        os.kill(self.pid, signal.SIGSTOP)


def send_request_to_take_snapshot():
    return Client.create().send_request_to_take_snapshot()



