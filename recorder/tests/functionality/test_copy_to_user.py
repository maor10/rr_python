import os
import tempfile

def test_read_copy_to_user(kernel_module, record_events_context, get_recorded_events, get_copies_from_events):
    """
    Test normal copy to user
    """
    STR_TO_CHECK = b"a" * 10000

    with tempfile.TemporaryFile() as tmp_file:
        tmp_file.write(STR_TO_CHECK)
        tmp_file.seek(0)
        
        with record_events_context():
            read_size = os.read(tmp_file.fileno(), len(STR_TO_CHECK))

    events = get_recorded_events()
    
    assert len(read_size) == len(STR_TO_CHECK)

    copies = get_copies_from_events(events)
    assert len(copies) != 0

    copied_str = b"".join([copy.data for copy in copies])
    assert copied_str == STR_TO_CHECK

def test_getresuid_copy_to_user(kernel_module, record_events_context, get_recorded_events, get_copies_from_events):
    """
    Test put_user
    """
    with record_events_context():
        uids_from_syscall = os.getresuid()
    
    events = get_recorded_events()

    copies = get_copies_from_events(events)

    uids = [int.from_bytes(copy.data, "little") for copy in copies]
    assert len(copies) == 3

    assert tuple(uids) == uids_from_syscall
