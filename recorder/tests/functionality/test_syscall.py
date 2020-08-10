import os
import select
import tempfile
import ctypes

__NR_GETDENTS = 78
__NR_GETDENTS64 = 217


def get_sum_of_memory_copies_lengths(syscall):
    """
    Return the sum of copies a syscall does.
    This function also check dups, meaning if 2 writes write
    to the same place, it will only count the first write
    """
    written_bytes_offsets = set()
    for copy in syscall.memory_copies:
        for index in range(len(copy.buffer)):
            written_bytes_offsets.add(copy.to_address + index)

    return len(written_bytes_offsets)

def test_read(kernel_module, record_syscalls_context, get_recorded_syscalls):
    with open("/dev/urandom") as f, record_syscalls_context():
        read_size = os.read(f.fileno(), 100)
        
    syscalls = get_recorded_syscalls()
    
    assert len(read_size) == 100

    assert len(syscalls) == 1
    assert syscalls[0].name == "read"
    assert syscalls[0].return_value == 100
    assert get_sum_of_memory_copies_lengths(syscalls[0]) == 100
    
def test_write(kernel_module, record_syscalls_context, get_recorded_syscalls):
    
    with open("/dev/null", "wb") as f:
        with record_syscalls_context():
            ret = os.write(f.fileno(), b"F" * 100)
    
    syscalls = get_recorded_syscalls()

    assert ret == 100
    
    assert len(syscalls) == 1
    assert syscalls[0].name == "write"
    assert syscalls[0].return_value == 100
    assert get_sum_of_memory_copies_lengths(syscalls[0]) == 0

def test_poll(kernel_module, record_syscalls_context, get_recorded_syscalls):
    with open("/dev/urandom", "rb") as f:
        poll_obj = select.poll()
        poll_obj.register(f, select.POLLIN)

        with record_syscalls_context():
            ret = poll_obj.poll(1)
    
    syscalls = get_recorded_syscalls()

    assert len(ret) == 1
    assert ret[0][1] == select.POLLIN

    assert len(syscalls) == 1
    assert syscalls[0].name == "poll"
    assert syscalls[0].return_value > 0
    assert get_sum_of_memory_copies_lengths(syscalls[0]) == 1


def test_getdents(kernel_module, record_syscalls_context, get_recorded_syscalls, syscall_caller):
    """
    Create an emptry dir and run getdents on it to check recorder
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_fd = os.open(tmp_dir, os.O_RDONLY | os.O_DIRECTORY)

        syscall_caller.restype = ctypes.c_int
        syscall_caller.argtypes = \
            ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_char), ctypes.c_uint

        getdents_res = ctypes.ARRAY(ctypes.c_char, 0xffff)()
        bytes_before = getdents_res.raw

        with record_syscalls_context():
            syscall_ret = syscall_caller(__NR_GETDENTS, tmp_dir_fd, getdents_res, len(getdents_res))
    
    syscalls = get_recorded_syscalls()

    assert len(syscalls) == 1
    assert syscalls[0].name == "getdents"
    assert syscalls[0].return_value > 0


    bytes_after = getdents_res.raw
    bytes_changed_count = len([True for index, byte in enumerate(bytes_before) if byte != bytes_after[index]])
    assert bytes_changed_count == get_sum_of_memory_copies_lengths(syscalls[0])

def test_getdents64(kernel_module, record_syscalls_context, get_recorded_syscalls, syscall_caller):
    """
    Create an emptry dir and run getdents64 on it to check recorder
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_fd = os.open(tmp_dir, os.O_RDONLY | os.O_DIRECTORY)

        syscall_caller.restype = ctypes.c_int
        syscall_caller.argtypes = \
            ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_char), ctypes.c_uint

        getdents_res = ctypes.ARRAY(ctypes.c_char, 0xffff)()
        bytes_before = getdents_res.raw

        with record_syscalls_context():
            syscall_ret = syscall_caller(__NR_GETDENTS64, tmp_dir_fd, getdents_res, len(getdents_res))
    
    syscalls = get_recorded_syscalls()

    assert len(syscalls) == 1
    assert syscalls[0].name == "getdents64"
    assert syscalls[0].return_value > 0


    bytes_after = getdents_res.raw
    bytes_changed_count = len([True for index, byte in enumerate(bytes_before) if byte != bytes_after[index]])
    assert bytes_changed_count == get_sum_of_memory_copies_lengths(syscalls[0])