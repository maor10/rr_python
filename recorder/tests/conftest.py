import pytest
import os
import contextlib
import psutil
from subprocess import check_output, check_call
from replayer.loader.system_call_loader import Loader

KERNEL_MODULE = "record.ko"
KERNEL_MODULE_PATH = f"../src/{KERNEL_MODULE}"
READ_SIZE = 0xffff

@pytest.fixture
def get_recorded_syscalls():
    def get():
        fd = os.open("/proc/syscall_dumper", os.O_RDONLY | os.O_NONBLOCK)

        content = b""
        cur_read = os.read(fd, READ_SIZE)
        while cur_read:
            content += cur_read
            cur_read = os.read(fd, READ_SIZE)
        
        return Loader.from_buffer(content).load_system_calls()[:-2] # Last 2 syscalls are lseek and close 

    return get
        
@pytest.fixture
def record_syscalls_context():
    @contextlib.contextmanager
    def _record_syscalls():
        with open("/proc/recorded_process", "w") as f:
            f.write(str(os.getpid()))
            try:
                f.flush()
                yield
            finally:
                f.seek(0)
                f.write("0")
                f.flush()
    return _record_syscalls

@pytest.fixture
def kernel_module_context():
    @contextlib.contextmanager
    def _kernel_module_context():
        assert check_call(["sudo", "insmod", KERNEL_MODULE_PATH]) == 0
        try:
            yield
        finally:
            assert check_call(["sudo", "rmmod", KERNEL_MODULE]) == 0
    return _kernel_module_context

@pytest.fixture
def kernel_module(kernel_module_context):
    with kernel_module_context():
        yield

@pytest.fixture
def whitelist_dmesg_context():
    @contextlib.contextmanager
    def _whitelist_dmesg_context(whitelist : list):
        # Clear dmesg before yielding
        check_output(["sudo", "dmesg", "-c"])

        yield

        dmesg_after = check_output(["sudo", "dmesg", "-c"]).decode('ascii').strip()
        for line in dmesg_after.split("\n"):
            assert len([True for x in whitelist if x in line]) == 1, \
                                        f"Line '{line}' not in whitelist"
    
    return _whitelist_dmesg_context
