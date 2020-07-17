import os


def write_to_recorded_process(b: bytes):
    try:
        with open('/proc/recorded_process', 'wb') as f:
            f.write(b)
    except OSError as o:
        # TODO fix kernel module recorded_processes_loader.c so we won't get hit with this
        pass


def start_recording():
    write_to_recorded_process(f"{os.getpid()}".encode('utf-8'))


def stop_recording():
    write_to_recorded_process(b"0")
