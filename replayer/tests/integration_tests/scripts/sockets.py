import socket
import sys
import interruptingcow
from pyrecorder import record
import time


@record
def connect_send_recv():
    host = sys.argv[1]
    port = int(sys.argv[2])
    text = sys.argv[3].encode('utf-8')
    s = socket.socket()
    start_time = time.time()
    while True:
        try:
            s.connect((host, port))
            s.send(text)
            received = s.recv(len(text))
            if received != text:
                # we don't do assert because on fail it makes system calls that cause invalidsyscall to appear,
                # covering up the issue
                print(f"received was {received}, expected {text}", file=sys.stderr)
                exit(1)
            break
        except socket.error:
            if time.time() - start_time > 1:
                raise
            time.sleep(0.3)


if __name__ == '__main__':
    connect_send_recv()