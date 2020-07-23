import os
import signal
from pathlib import Path

import pytest

import creplayer
from replayer.loader import Registers


def test_write_and_read_from_tracee_happy_flow(run_test_binary):
    process = run_test_binary(str(Path(__file__).parent / 'binary_scripts'), 'allocate_buffer.c')
    line = process.stdout.readline().decode('utf-8').strip()
    address = int(line)

    value = b'Hello! I would like to introduce myself. My name is Yolanda, the richest woman in the south sea. For many years,' \
            b'I have studied the hypocrisy that is YOUR mother. My dear reader. Your mother is a joke, an imbecile, a continuous monument' \
            b'to the fact that humanity can never know when it has reached it\'s lowest point.'

    creplayer.attach_to_tracee_and_begin(process.pid)
    creplayer.write_to_tracee(process.pid, address, value)
    assert creplayer.read_from_tracee(process.pid, address, len(value)) == value


def test_read_from_tracee_in_invalid_address_raises_system_error(run_test_binary):
    process = run_test_binary(str(Path(__file__).parent / 'binary_scripts'), 'allocate_buffer.c')

    creplayer.attach_to_tracee_and_begin(process.pid)

    with pytest.raises(SystemError):
        creplayer.read_from_tracee(process.pid, 0, 1000)


def test_read_write_registers(run_test_binary):
    process = run_test_binary(str(Path(__file__).parent / 'binary_scripts'), 'read.c')
    creplayer.attach_to_tracee_and_begin(process.pid)
    creplayer.run_until_enter_or_exit_of_next_syscall(process.pid)
    registers = Registers(*creplayer.get_registers_from_tracee(process.pid))
    creplayer.set_registers_in_tracee(process.pid, *registers.to_list())
    assert creplayer.get_registers_from_tracee(process.pid) == tuple(registers.to_list())


def test_run_until_enter_or_exit_of_next_syscall_happy_flow(run_test_binary):
    process = run_test_binary(str(Path(__file__).parent / 'binary_scripts'), 'read.c')
    creplayer.attach_to_tracee_and_begin(process.pid)
    creplayer.run_until_enter_or_exit_of_next_syscall(process.pid)
    registers = Registers(*creplayer.get_registers_from_tracee(process.pid))
    assert registers.sys_call == 0


def test_creplayer_did_tracee_segfault(run_test_binary):
    process = run_test_binary(str(Path(__file__).parent / 'binary_scripts'), 'should_segfault.c')
    creplayer.attach_to_tracee_and_begin(process.pid)
    creplayer.run_until_enter_or_exit_of_next_syscall(process.pid)
    assert creplayer.did_segfault(process.pid)
