import hwcounter
from replayer.loader import RDTSC_EVENT_ID


def test_rdtsc_functionality(kernel_module, record_events_context):
    before = hwcounter.count()
    with record_events_context():
        during = hwcounter.count()
    after = hwcounter.count()

    assert before < during < after, f"tick was: {during}"

def test_rdtsc_recorded(kernel_module, record_events_context, get_recorded_events):
    with record_events_context():
        counter = hwcounter.count()
    
    events = get_recorded_events()
    
    assert events[0].event_type == RDTSC_EVENT_ID

    assert events[0].event_data.ax == counter & 0xFFFFFFFF
    assert events[0].event_data.dx == counter >> 32