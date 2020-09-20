import select
import os
import tempfile
import ctypes


__NR_GETDENTS = 78
__NR_GETDENTS64 = 217

def get_bytes_changed_count(copies):
    """
    Return The amount of bytes changed in all received copies.
    This function also check dups, meaning if 2 writes write
    to the same place, it will only count the first write
    """
    return len({copy.to_addr + i for copy in copies for i in range(len(copy.data))})


def test_poll(kernel_module, record_events_context, get_recorded_events, get_copies_from_events):
    with open("/dev/urandom", "rb") as f:
        poll_obj = select.poll()
        poll_obj.register(f, select.POLLIN)

        with record_events_context():
            ret = poll_obj.poll(1)
    
    events = get_recorded_events()

    assert len(ret) == 1
    assert ret[0][1] == select.POLLIN

    copies = get_copies_from_events(events)
    assert len(copies) == 1
    assert int.from_bytes(copies[0].data, "little") == select.POLLIN

def test_getdents(kernel_module, record_events_context, get_recorded_events, syscall_caller, get_copies_from_events):
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

        with record_events_context():
            syscall_ret = syscall_caller(__NR_GETDENTS, tmp_dir_fd, getdents_res, len(getdents_res))
        bytes_after = getdents_res.raw
    

    events = get_recorded_events()
    copies = get_copies_from_events(events) 
    bytes_changed_count_from_record = get_bytes_changed_count(copies)

    bytes_changed_count = len([1 for index, byte in enumerate(bytes_before) if byte != bytes_after[index]])
    assert bytes_changed_count == bytes_changed_count_from_record


def test_getdents64(kernel_module, record_events_context, get_recorded_events, syscall_caller, get_copies_from_events):
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

        with record_events_context():
            syscall_ret = syscall_caller(__NR_GETDENTS64, tmp_dir_fd, getdents_res, len(getdents_res))
        bytes_after = getdents_res.raw

    events = get_recorded_events()
    copies = get_copies_from_events(events) 
    bytes_changed_count_from_record = get_bytes_changed_count(copies)

    bytes_changed_count = len([1 for index, byte in enumerate(bytes_before) if byte != bytes_after[index]])
    assert bytes_changed_count == bytes_changed_count_from_record
