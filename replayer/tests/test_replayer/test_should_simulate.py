import pytest

from replayer.consts import SYS_CALL_REGISTER
from replayer.should_simulate import MMAP_SYSTEM_CALL_NUMBER, should_simulate_system_call
from replayer.system_call_runners.regular_system_call_runner.system_call_definitions.fs_system_call_definitions import \
    open_system_call_definition, close_system_call_definition
from replayer.system_calls import SystemCall

from replayer.system_calls.exceptions import CouldNotFindMatchingSyscallException


def create_open_system_call_for_fd(fd: int) -> SystemCall:
    return SystemCall(
        memory_copies=[],
        registers={
            SYS_CALL_REGISTER: open_system_call_definition.system_call_number
        },
        return_value=fd
    )


def create_mmap_system_call_for_fd(fd: int) -> SystemCall:
    return SystemCall(
        memory_copies=[],
        registers={
            SYS_CALL_REGISTER: MMAP_SYSTEM_CALL_NUMBER,
            'r8': fd
        },
        return_value=0
    )


def create_close_call_for_fd(fd: int) -> SystemCall:
    return SystemCall(
        memory_copies=[],
        registers={
            SYS_CALL_REGISTER: close_system_call_definition.system_call_number,
            'rdi': fd
        },
        return_value=0
    )


@pytest.mark.parametrize('name, system_calls, expected_should_simulates', [
    ('no mmaps', [
         create_open_system_call_for_fd(3),
         create_close_call_for_fd(3)
     ], [
         True, True
     ]),
    ('only file is an mmaped file', [
         create_open_system_call_for_fd(3),
         create_mmap_system_call_for_fd(3),
         create_close_call_for_fd(3)
     ], [
         False, False, False
     ]),
    ('one file is mmaped, one file is just opened without mmap', [
         create_open_system_call_for_fd(3),
         create_open_system_call_for_fd(4),
         create_mmap_system_call_for_fd(3),
         create_close_call_for_fd(4),
         create_close_call_for_fd(3)
     ], [
         False, True, False, True, False
     ]),
    ('same fd reused for mmap after close (first time without mmap)', [
         create_open_system_call_for_fd(3),
         create_close_call_for_fd(3),
         create_open_system_call_for_fd(3),
         create_mmap_system_call_for_fd(3),
         create_close_call_for_fd(3)
     ], [
         True, True, False, False, False
     ]),
    ("same fd reused after mmap's fd was closed", [
         create_open_system_call_for_fd(3),
         create_mmap_system_call_for_fd(3),
         create_close_call_for_fd(3),
         create_open_system_call_for_fd(3),
         create_close_call_for_fd(3)
     ], [
         False, False, False, True, True
     ]),
    ('open without close with mmap', [
         create_open_system_call_for_fd(3),
         create_mmap_system_call_for_fd(3)
     ], [
         False, False
     ]),
    ('open without close without mmap', [
         create_open_system_call_for_fd(3),
     ], [
         True
     ])

])
def test_get_replayable_system_calls(name, system_calls, expected_should_simulates):
    for i, (system_call, expected_should_simulate) in enumerate(zip(system_calls, expected_should_simulates)):
        assert should_simulate_system_call(system_calls, i) == expected_should_simulate, f'failed "{name}" index {i}'


def test_close_without_open_raises_exception():
    with pytest.raises(CouldNotFindMatchingSyscallException):
        should_simulate_system_call([create_close_call_for_fd(1)], 0)
