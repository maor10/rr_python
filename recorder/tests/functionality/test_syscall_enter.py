import os

from replayer.loader import SYSTEM_CALL_ENTER_EVENT_ID

def test_read_enter(kernel_module, record_events_context, get_recorded_events):
    with open("/dev/urandom") as f, record_events_context():
        read_size = os.read(f.fileno(), 100)
        
    events = get_recorded_events()
    
    assert len(read_size) == 100

    assert events[0].event_type == SYSTEM_CALL_ENTER_EVENT_ID
    assert events[0].event_data.name == "read"
    assert events[0].event_data.registers.rdx == 100

    
def test_write_enter(kernel_module, record_events_context, get_recorded_events):
    
    with open("/dev/null", "wb") as f:
        with record_events_context():
            ret = os.write(f.fileno(), b"F" * 100)
    
    events = get_recorded_events()

    assert ret == 100

    assert events[0].event_type == SYSTEM_CALL_ENTER_EVENT_ID
    assert events[0].event_data.name == "write"
    assert events[0].event_data.registers.rdx == 100
