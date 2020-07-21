from pyrecorder import record
import ssl


@record
def generate_random():
    print(ssl.RAND_bytes(10000))


if __name__ == '__main__':
    generate_random()
