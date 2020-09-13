import os

def test_write_done(kernel_module, record_events_context, get_recorded_events):
    with open("/dev/null", "wb") as f:
        with record_events_context():
            ret = os.write(f.fileno(), b"F" * 100)

    events = get_recorded_events()

    assert ret == 100

    assert events[1].event_type == 2
    assert events[1].event_data.ret == 100