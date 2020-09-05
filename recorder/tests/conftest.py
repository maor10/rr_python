import pytest
import os
import contextlib
import psutil
import subprocess
from typing import List
from replayer.loader import EventLoader

KERNEL_MODULE = "record.ko"
KERNEL_MODULE_PATH = f"../src/{KERNEL_MODULE}"
READ_SIZE = 0xffff

START_RECORD_ME = b"1"
STOP_RECORD_ME = b"0"


@pytest.fixture
def get_recorded_events():
    def get():
        fd = os.open("/proc/events_dump", os.O_RDONLY | os.O_NONBLOCK)

        content = b""
        current_read = os.read(fd, READ_SIZE)
        while current_read:
            content += current_read
            current_read = os.read(fd, READ_SIZE)
        
        # First syscall is close of /proc/record_command, 
        # And last 2 are open and write to that file. Don't return them!
        return EventLoader.from_buffer(content).load_many()[1:-2]
        
    return get
        
def send_record_command(command):
    fd = os.open("/proc/record_command", os.O_WRONLY)
    try:
        os.write(fd, command)
    finally:
        os.close(fd)

@pytest.fixture
def record_events_context():
    @contextlib.contextmanager
    def _record_syscalls():
        send_record_command(START_RECORD_ME)
        try:
            yield
        finally:
            send_record_command(STOP_RECORD_ME)
    return _record_syscalls

@pytest.fixture
def kernel_module_context():
    @contextlib.contextmanager
    def _kernel_module_context():
        subprocess.check_call(["sudo", "insmod", KERNEL_MODULE_PATH])
        try:
            yield
        finally:
            subprocess.check_call(["sudo", "rmmod", KERNEL_MODULE])
    return _kernel_module_context

@pytest.fixture
def kernel_module(kernel_module_context):
    with kernel_module_context():
        yield

@pytest.fixture
def whitelist_dmesg_context():
    @contextlib.contextmanager
    def _whitelist_dmesg_context(whitelist : List[str]):
        # Clear dmesg before yielding
        subprocess.check_output(["sudo", "dmesg", "-c"])

        yield

        dmesg_after = subprocess.check_output(["sudo", "dmesg", "-c"]).decode('ascii').strip()
        for line in dmesg_after.split("\n"):
            assert len([True for record in whitelist if record in line]) == 1, \
                                        f"Line '{line}' not in whitelist"
    
    return _whitelist_dmesg_context
