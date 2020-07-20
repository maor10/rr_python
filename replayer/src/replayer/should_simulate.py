from typing import List, Callable, Union

from replayer.system_calls.system_call import SystemCall
from replayer.system_call_runners import SystemCallRunner
from replayer.system_calls.exceptions import CouldNotFindMatchingSyscallException
from replayer.system_call_runners.regular_system_call_runner.system_call_definitions.fs_system_call_definitions import open_system_call_definition, \
    openat_system_call_definition, close_system_call_definition
from replayer.system_call_runners.regular_system_call_runner.system_call_definitions.socket_system_call_definitions \
    import socket_system_call_definition


FS_OPEN_SYSTEM_CALLS_DEFINITIONS = [open_system_call_definition, openat_system_call_definition,
                                    socket_system_call_definition]
FS_OPEN_SYSTEM_CALL_NUMBERS = [open_system_call.system_call_number
                               for open_system_call in FS_OPEN_SYSTEM_CALLS_DEFINITIONS]

MMAP_SYSTEM_CALL_NUMBER = 9


def _find_first_syscall_matching(system_calls, matcher_callback: Callable, raise_if_not_found=True) -> Union[None,
                                                                                                             SystemCall]:
    """
    Find the first sys call which returns true on a matcher lambda func

    :param system_calls: a list of system calls to go through
    :param matcher_callback: function to match the system call
    :param raise_if_not_found: whether or not to raise an exception if the system call isn't found

    :return: System Call or None

    :raise CouldNotFindMatchingSyscallException if raise_if_not_found is True and no sys call was found
    """
    system_call = next((system_call for system_call in system_calls if matcher_callback(system_call)), None)
    if system_call is None and raise_if_not_found:
        raise CouldNotFindMatchingSyscallException()
    return system_call


def _is_open_system_call_for_fd(system_call: SystemCall, fd: int):
    """
    Returns whether the system call is an 'open' sys call that gives back a given fd

    Note: the return value of open is the fd

    :param system_call: to check
    :param fd: fd to check if opening
    :return: whether or not it's a 'open' syscall on fd
    """
    return system_call.num in FS_OPEN_SYSTEM_CALL_NUMBERS and system_call.return_value == fd


def _is_close_system_call_for_fd(system_call: SystemCall, fd: int):
    """
    Returns whether the system call is a 'close' sys call for a given fd

    Note: 'rdi' is the register in the syscall which should contain the fd

    :param system_call: to check
    :param fd: fd to check if closing
    :return: whether or not it's a 'close' syscall on fd
    """
    return system_call.num == close_system_call_definition.system_call_number and system_call.registers['rdi'] == fd


def _is_mmap_system_call_for_fd(system_call: SystemCall, fd: int):
    """
    Returns whether the system call is an 'mmap' sys call for a given fd

    Note: 'r8' is the register in the syscall which should contain the fd

    :param system_call: to check
    :param fd: fd to check if mmaping
    :return: whether or not it's a 'mmap' syscall on fd
    """
    return system_call.num == MMAP_SYSTEM_CALL_NUMBER and system_call.registers['r8'] == fd


def _fd_appears_in_mmap_before_close(fd: int, system_calls: List[SystemCall], system_call_index: int):
    system_call = _find_first_syscall_matching(system_calls[system_call_index:],
                                               matcher_callback=lambda s: (_is_close_system_call_for_fd(s, fd)
                                                                          or _is_mmap_system_call_for_fd(s, fd)),
                                               raise_if_not_found=False)
    return system_call is not None and system_call.num == MMAP_SYSTEM_CALL_NUMBER


def _mmap_appears_after_open_for_fd(fd: int, system_calls: List[SystemCall], system_call_index: int):
    system_call = _find_first_syscall_matching(reversed(system_calls[:system_call_index]),
                                               matcher_callback=lambda s: (_is_open_system_call_for_fd(s, fd)
                                                                           or _is_mmap_system_call_for_fd(s, fd)),
                                               raise_if_not_found=False)
    return system_call is not None and system_call.num == MMAP_SYSTEM_CALL_NUMBER


def _should_simulate_open_system_call(system_calls, system_call, system_call_index):
    return not _fd_appears_in_mmap_before_close(system_call.return_value, system_calls, system_call_index)


def _should_simulate_close_system_call(system_calls, system_call, system_call_index):
    return not _mmap_appears_after_open_for_fd(system_call.registers['rdi'],  # rdi is register of the fd for close
                                               system_calls, system_call_index)


def should_simulate_system_call(system_calls: List[SystemCall], system_call_index: int) -> bool:
    """
    Should a syscall at a given index be simulated?


    :param system_calls: all the system calls in a given session
    :param system_call_index: the index of the syscall to check if it should be simulated

    :return: whether it should be simulated
    """
    system_call = system_calls[system_call_index]
    handler = {
        openat_system_call_definition.system_call_number: lambda *_: False, #_should_simulate_open_system_call,
        open_system_call_definition.system_call_number: lambda *_: False, #_should_simulate_open_system_call,
        close_system_call_definition.system_call_number: lambda *_: False, #_should_simulate_close_system_call,
        MMAP_SYSTEM_CALL_NUMBER: lambda *_: False,
        10: lambda *_: False,
        41: lambda *_: False
    }.get(system_call.num, lambda *_: True)
    return handler(system_calls, system_call, system_call_index)
