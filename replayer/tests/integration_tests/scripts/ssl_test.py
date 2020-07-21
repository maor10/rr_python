from pyrecorder import record
from test_ssl.main import get_random


@record
def record_get_random():
    print(get_random())


if __name__ == '__main__':
    record_get_random()
