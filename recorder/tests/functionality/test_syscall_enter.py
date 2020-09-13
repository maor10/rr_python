import os

def test_read_enter(kernel_module, record_events_context, get_recorded_events):
    with open("/dev/urandom") as f, record_events_context():
        read_size = os.read(f.fileno(), 100)
        
    events = get_recorded_events()
    
    assert len(read_size) == 100

    assert events[0].event_type == 1
    assert events[0].event_data.name == "read"
    assert events[0].event_data.registers.rdx == 100

    
def test_write_enter(kernel_module, record_events_context, get_recorded_events):
    
    with open("/dev/null", "wb") as f:
        with record_events_context():
            ret = os.write(f.fileno(), b"F" * 100)
    
    events = get_recorded_events()

    assert ret == 100

    assert events[0].event_type == 1
    assert events[0].event_data.name == "write"
    assert events[0].event_data.registers.rdx == 100

# def test_getdents64(kernel_module, record_syscalls_context, get_recorded_syscalls, syscall_caller):
#     """
#     Create an emptry dir and run getdents64 on it to check recorder
#     """
#     with tempfile.TemporaryDirectory() as tmp_dir:
#         tmp_dir_fd = os.open(tmp_dir, os.O_RDONLY | os.O_DIRECTORY)

#         syscall_caller.restype = ctypes.c_int
#         syscall_caller.argtypes = \
#             ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_char), ctypes.c_uint

#         getdents_res = ctypes.ARRAY(ctypes.c_char, 0xffff)()
#         bytes_before = getdents_res.raw

#         with record_syscalls_context():
#             syscall_ret = syscall_caller(__NR_GETDENTS64, tmp_dir_fd, getdents_res, len(getdents_res))
    
#     syscalls = get_recorded_syscalls()

#     assert len(syscalls) == 1
#     assert syscalls[0].name == "getdents64"
#     assert syscalls[0].return_value > 0


#     bytes_after = getdents_res.raw
#     bytes_changed_count = len([1 for index, byte in enumerate(bytes_before) if byte != bytes_after[index]])
#     assert bytes_changed_count == get_sum_of_memory_copies_lengths(syscalls[0])"