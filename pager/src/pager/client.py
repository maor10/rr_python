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


if __name__ == '__main__':
    import random
    print("generating random...")
    x = []
    for i in range(1000 * 10000):
        x.append(random.randint(0, 100))
    print("starting...")
    # print(os.getpid())
    # time.sleep(100000)
    client = Client.create()
    start_time = time.time()
    client.send_request_to_take_snapshot()
    end_time = time.time()
    print(f"TIME {end_time - start_time}")
    # Randomly print to file to restore acting appropriately
    for i in range(30):
        time.sleep(1)
        with open('/tmp/play.txt', 'a') as f:
            f.write(f'{i}\n')
    print("Finished execution")


