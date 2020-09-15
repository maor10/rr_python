import os
import time
import pytest

from multiprocessing import Process
from interruptingcow import timeout

def test_events_procfile_work(kernel_module, record_events_context):
    with record_events_context():
        os.stat("/dev/null")

    fd = os.open("/proc/events_dump", os.O_RDONLY)
    events = os.read(fd, 10000)
    os.close(fd)
    
    assert len(events) != 0


def test_events_procfile_noblock_work(kernel_module, record_events_context):
    with record_events_context():
        os.stat("/dev/null")

    fd = os.open("/proc/events_dump", os.O_RDONLY | os.O_NONBLOCK)
    events = os.read(fd, 10000)
    os.close(fd)
    
    assert len(events) != 0


def test_events_procfile_noblock_ret_empty(kernel_module):
    fd = os.open("/proc/events_dump", os.O_RDONLY | os.O_NONBLOCK)
    events = os.read(fd, 10000)
    os.close(fd)
    
    assert len(events) == 0

def test_events_procfile_ret_blocking(kernel_module):
    class TimeoutException(BaseException):
        pass

    fd = os.open("/proc/events_dump", os.O_RDONLY)
    
    with pytest.raises(TimeoutException):
        with timeout(seconds=1, exception=TimeoutException):
            events = os.read(fd, 10000)
    
    os.close(fd)
    

def test_events_procfile_stop_blocking_on_event(kernel_module, record_events_context):
    def sleep_and_record_event(sleep_time, record_events_context):
        time.sleep(sleep_time)
        with record_events_context():
            os.stat("/dev/null")

    p = Process(target=sleep_and_record_event, args=(1, record_events_context))
    p.start()

    fd = os.open("/proc/events_dump", os.O_RDONLY)

    with timeout(seconds=3):
        events = os.read(fd, 10000)
    
    os.close(fd)

    assert len(events) != 0


def test_events_procfile_shortread_no_data_lose(kernel_module, record_events_context):
    with record_events_context():
        os.stat("/dev/null")

    fd = os.open("/proc/events_dump", os.O_RDONLY)
    with pytest.raises(OSError):
        events = os.read(fd, 1)
    
    events = os.read(fd, 1000)
    os.close(fd)
    
    assert len(events) != 0