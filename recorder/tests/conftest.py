import pytest
import os
import contextlib
import psutil
from subprocess import check_output, check_call

KERNEL_MODULE = "record.ko"
KERNEL_MODULE_PATH = f"../src/{KERNEL_MODULE}"

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

MAX_MEM_DIFF = 20000000

# TODO: Maybe use kmemlean?
@pytest.fixture
def mem_leak_finder_context():
    @contextlib.contextmanager
    def _mem_leak_finder_context():
        mem_before = psutil.virtual_memory().free
        yield
        diff = psutil.virtual_memory().free - mem_before

        assert diff < MAX_MEM_DIFF
    
    return _mem_leak_finder_context
