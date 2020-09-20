import os
import pytest
import ctypes

from replayer.loader import SYSTEM_CALL_DONE_EVENT_ID
from multiprocessing import Process
from functools import partial

def test_write_done(kernel_module, record_events_context, get_recorded_events):
    with open("/dev/null", "wb") as f:
        with record_events_context():
            ret = os.write(f.fileno(), b"F" * 100)

    events = get_recorded_events()

    assert ret == 100

    assert events[1].event_type == SYSTEM_CALL_DONE_EVENT_ID
    assert events[1].event_data.ret == 100

@pytest.mark.parametrize("syscall", [
    partial(os._exit, status=0),
    partial(ctypes.CDLL(None).syscall, 60, 0),
    # We want to fake execve call
    partial(os.execve, "/bin/fakepath", ["fakepath"], {})
])
def test_exit_syscall_no_done(kernel_module, record_events_context, get_recorded_events, syscall):
    def record_and_exit(record_events_context, syscall):
        with record_events_context():
            try:
                syscall()
            except:
                pass

    p = Process(target=record_and_exit, args=(record_events_context, syscall))
    p.start()
    p.join()

    events = get_recorded_events()
    assert len([1 for event in events if event.event_type == SYSTEM_CALL_DONE_EVENT_ID]) == 0
    
    # Test events are read normally after
    with record_events_context():
        os.stat("/dev/null")
    
    events = get_recorded_events()
    assert len([1 for event in events if event.event_type == SYSTEM_CALL_DONE_EVENT_ID]) == 1
 
#TODO: ADD TEST WHERE SYS_EXIT IS CALLED :(