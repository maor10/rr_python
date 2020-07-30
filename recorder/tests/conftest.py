import pytest
import os
import contextlib
import psutil
import subprocess
from typing import List
from replayer.loader.system_call_loader import Loader

KERNEL_MODULE = "record.ko"
KERNEL_MODULE_PATH = f"../src/{KERNEL_MODULE}"
READ_SIZE = 0xffff


@pytest.fixture
def get_recorded_syscalls():
    def get():
        fd = os.open("/proc/syscall_dumper", os.O_RDONLY | os.O_NONBLOCK)

        content = b""
        current_read = os.read(fd, READ_SIZE)
        while current_read:
            content += current_read
            current_read = os.read(fd, READ_SIZE)
        
        # First syscall is close of /proc/recorded_process, 
        # And last 2 are open and write to that file. Don't return them!
        return Loader.from_buffer(content).load_system_calls()[1:-2]

    return get
        
def start_record_pid(pid):
    fd = os.open("/proc/recorded_process", os.O_WRONLY)
    try:
        os.write(fd, str(pid).encode())
    finally:
        os.close(fd)

@pytest.fixture
def record_syscalls_context():
    @contextlib.contextmanager
    def _record_syscalls():
        start_record_pid(os.getpid())
        try:
            yield
        finally:
            start_record_pid(0) # Stop the recording
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
