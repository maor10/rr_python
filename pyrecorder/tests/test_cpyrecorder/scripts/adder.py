import os
import signal

from pyrecorder import record
import pager


# MONKEYPATCH PAGER SO WE DON'T NEED THE PROCESS

pager.send_request_to_take_snapshot = lambda: os.kill(os.getpid(), signal.SIGSTOP)


@record
def adder():
    print("FUNNNN")
    f = open('/tmp/a.txt', 'w')
    f.write('shamalalala')
    f.flush()
    return 2 + 2


adder()
