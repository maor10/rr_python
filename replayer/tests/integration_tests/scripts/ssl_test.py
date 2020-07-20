from pyrecorder import record
from test_ssl.main import get_random


def cc():
    pass


@record
def record_get_random():
    print(get_random())


record_get_random()
