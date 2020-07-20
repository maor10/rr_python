

import ctest_ssl

from pyrecorder import record


def get_random():
    return f"RANDOM IS {ctest_ssl.run_random()}"


if __name__ == '__main__':
    get_random()
