import os
import select

def syscall_sum_copies(syscall):
    return sum(len(copy.buffer) for copy in syscall.memory_copies)

def test_read(kernel_module, record_syscalls_context, get_recorded_syscalls):
    with open("/dev/urandom") as f:
        with record_syscalls_context():
            ret = os.read(f.fileno(), 100)
        
    syscalls = get_recorded_syscalls()
    
    assert len(ret) == 100

    assert len(syscalls) == 1
    assert syscalls[0].name == "read"
    assert syscalls[0].return_value == 100
    assert syscall_sum_copies(syscalls[0]) == 100
    
def test_write(kernel_module, record_syscalls_context, get_recorded_syscalls):
    
    with open("/dev/null", "wb") as f:
        with record_syscalls_context():
            ret = os.write(f.fileno(), b"F" * 100)
    
    syscalls = get_recorded_syscalls()

    assert ret == 100
    
    assert len(syscalls) == 1
    assert syscalls[0].name == "write"
    assert syscalls[0].return_value == 100
    assert syscall_sum_copies(syscalls[0]) == 0

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
    assert syscall_sum_copies(syscalls[0]) == 1
