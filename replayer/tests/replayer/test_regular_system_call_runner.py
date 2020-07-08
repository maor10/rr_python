import pytest

from replayer.exceptions import NoSuchSysCallRunnerExistsException
from replayer.system_call import SystemCall
from replayer.system_call.memory_copy import MemoryCopy


@pytest.mark.parametrize('buffer', [
    b"hello world",  # check when there will be leftover from word
    b"hello worldaaaa",  # check when length will be 16 bytes
])
def test_replayer_read_happy_flow(buffer, run_system_calls_on_binary):
    buffer_addr = 1111
    length = len(buffer)
    fd = -1

    run_system_calls_on_binary(binary_name='read',
                               arguments_for_binary=[str(length), str(length), buffer],
                               system_call_numbers_to_handle=[0],
                               system_calls=[
                                   SystemCall(
                                       registers=dict(
                                           orig_ax=0,
                                           rdi=fd,
                                           rsi=buffer_addr,
                                           rdx=length
                                       ),
                                       memory_copies=[
                                           MemoryCopy(
                                               from_address=0,
                                               to_address=buffer_addr,
                                               buffer=bytes(buffer) + b'\0'
                                           )
                                       ],
                                       return_value=length
                                   )
                               ]
                               )


def test_replayer_fails_gracefully_with_no_sys_calls(run_system_calls_on_binary):
    with pytest.raises(NoSuchSysCallRunnerExistsException):
        run_system_calls_on_binary(binary_name='read',
                                   arguments_for_binary=['5', '5', b"ddd"],
                                   system_call_numbers_to_handle=[0],
                                   system_calls=[])


def test_replayer_read_with_multiple_copies(run_system_calls_on_binary):
    buffer = b"hello my good lady"
    buffer_addr = 1111
    length = len(buffer)
    fd = -1

    run_system_calls_on_binary(binary_name='read',
                               arguments_for_binary=[str(length), str(length), buffer],
                               system_call_numbers_to_handle=[0],
                               system_calls=[
                                   SystemCall(
                                       registers=dict(
                                           orig_ax=0,
                                           rdi=fd,
                                           rsi=buffer_addr,
                                           rdx=length
                                       ),
                                       memory_copies=[
                                           MemoryCopy(
                                               from_address=0,
                                               to_address=buffer_addr,
                                               buffer=buffer[:7]
                                           ),
                                           MemoryCopy(
                                               from_address=4444,
                                               to_address=buffer_addr + 7,
                                               buffer=buffer[7:10]
                                           ),
                                           MemoryCopy(
                                               from_address=2222,
                                               to_address=buffer_addr + 10,
                                               buffer=buffer[10:]
                                           )
                                       ],
                                       return_value=length
                                   )
                               ]
                               )


def test_replayer_read_on_stack_does_not_crash(run_system_calls_on_binary):
    buffer = b"hell"
    buffer_addr = 1111
    length = len(buffer) + 1
    fd = -1

    run_system_calls_on_binary(binary_name='read_in_stack_five_bytes',
                               arguments_for_binary=[str(length), str(length), buffer],
                               system_call_numbers_to_handle=[0],
                               system_calls=[
                                   SystemCall(
                                       registers=dict(
                                           orig_ax=0,
                                           rdi=fd,
                                           rsi=buffer_addr,
                                           rdx=length
                                       ),
                                       memory_copies=[
                                           MemoryCopy(
                                               from_address=0,
                                               to_address=buffer_addr,
                                               buffer=buffer + b'\0'
                                           )
                                       ],
                                       return_value=length
                                   )
                               ]
                               )