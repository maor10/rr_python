from typing import List, Callable, Dict
import creplayer
from replayer import syscall_handlers, system_consts
from replayer.system_consts import REGISTER_NAMES, EXIT_GROUP_SYS_CALL
from .exceptions import UnexpectedSysCallException, UnexpectedRegistersException, \
    UnexpectedSystemCallReturnValueException
from replayer.should_simulate import should_simulate_system_call
from replayer.loader import SystemCall
from replayer.loader.system_call_loader import Loader
from replayer.tracing_exceptions import SegfaultException
from .loader.registers import Registers


# TODO: remove temporary hack which ignores validating certain sys calls because one of their registers is
# an fd that could be different in record and replay
SYS_CALLS_TO_IGNORE_IN_VALIDATION = [system_consts.READ_SYS_CALL, system_consts.CLOSE_SYS_CALL,
                                     system_consts.FSTAT_SYS_CALL, system_consts.MMAP_SYS_CALL,
                                     system_consts.MPROTECT_SYS_CALL, system_consts.OPENAT_SYS_CALL]


class Replayer:
    """
    Manages replaying a recording in a given process.
    The replayer attaches to a given process and places it in a "sandbox" whereby any access to
    outside resources will be either wrapped or simulated, in order to create the same exact execution described by the
    recording
    """

    def __init__(self, pid: int, system_calls: List[SystemCall], stdout_callback=None):
        self.pid = pid
        self.system_calls = system_calls
        self.stdout_callback = stdout_callback

    @staticmethod
    def get_new_register_values_for_system_call(recorded_system_call: SystemCall, registers: Registers) \
            -> Registers:
        handler = syscall_handlers.HANDLERS.get(recorded_system_call.num)
        new_register_values = handler(recorded_system_call, registers) if handler else registers
        return new_register_values

    @staticmethod
    def raise_on_unexpected_state(recorded_system_call: SystemCall, tracee_registers: Registers):
        if recorded_system_call.registers != tracee_registers \
                and recorded_system_call.num not in SYS_CALLS_TO_IGNORE_IN_VALIDATION:
            raise UnexpectedRegistersException(expected=recorded_system_call.registers,
                                               received=tracee_registers)
        if recorded_system_call.num != tracee_registers.sys_call:
            raise UnexpectedSysCallException(expected=recorded_system_call.num,
                                             received=tracee_registers.sys_call)

    @staticmethod
    def raise_on_unexpected_return_value(recorded_system_call: SystemCall, tracee_registers: Registers):
        if recorded_system_call.return_value != tracee_registers.rax \
                and recorded_system_call.num not in SYS_CALLS_TO_IGNORE_IN_VALIDATION:
            raise UnexpectedSystemCallReturnValueException(expected=recorded_system_call.return_value,
                                                           received=tracee_registers.rax)

    def _get_registers_from_tracee(self):
        registers_list = creplayer.get_registers_from_tracee(self.pid)
        return Registers(*registers_list)

    def copy_memory_copies_to_tracee(self, recorded_system_call: SystemCall):
        """
        Copy all the memory copies of a given system call to the tracee
        """
        for memory_copy in recorded_system_call.memory_copies:
            creplayer.write_to_tracee(self.pid, memory_copy.to_address, memory_copy.buffer)

    def call_stdout_callback_if_relevant(self, recorded_system_call: SystemCall):
        # rdi 1 is fd stdout
        if recorded_system_call.num == system_consts.WRITE_SYS_CALL and recorded_system_call.registers.rdi == 1 \
                and self.stdout_callback is not None:
            self.stdout_callback(creplayer.read_from_tracee(self.pid,
                                                            recorded_system_call.registers.rsi,
                                                            recorded_system_call.registers.rdx))

    def raise_on_tracee_segfault(self):
        if creplayer.did_segfault(self.pid):
            raise SegfaultException()

    def get_exit_status(self) -> int:
        """
        Get the tracees exit status
        """
        creplayer.run_until_enter_or_exit_of_next_syscall(self.pid)
        registers = self._get_registers_from_tracee()
        if registers.sys_call is not EXIT_GROUP_SYS_CALL:
            raise UnexpectedSysCallException(
                expected=EXIT_GROUP_SYS_CALL,
                received=registers.sys_call
            )
        creplayer.run_until_enter_or_exit_of_next_syscall(self.pid)
        return registers.rdi

    def simulate_system_call_for_tracee(self, recorded_system_call: SystemCall, tracee_registers: Registers):
        """
        Simulate the system call for the tracee. Recreate the behaviour the original system call did.

        :param recorded_system_call: to recreate in tracee
        :param tracee_registers: current tracee registers
        """
        # run an invalid syscall
        registers_for_invalid_sys_call = tracee_registers.copy()
        registers_for_invalid_sys_call.orig_rax = -5
        creplayer.set_registers_in_tracee(self.pid, *registers_for_invalid_sys_call.to_list())
        creplayer.run_until_enter_or_exit_of_next_syscall(self.pid)
        self.copy_memory_copies_to_tracee(recorded_system_call)
        new_registers = tracee_registers.copy()
        new_registers.rax = recorded_system_call.return_value
        creplayer.set_registers_in_tracee(self.pid, *new_registers.to_list())

    def wrap_and_run_real_system_call_in_tracee(self, recorded_system_call: SystemCall, tracee_registers: Registers):
        """
        Run real system call (no simulation) in tracee. We do this in situations where it is not possible to
        simulate the requested system call, but wrap it in order for the same behaviour to occur as in the recording
        from the tracee's point of view.

        For example, we cannot simulate MMAP appropriately, but we wrap it so that the mapped addresses will be the
        same as in the recording

        :param recorded_system_call: the equivalent system call in the recording
        :param tracee_registers: current tracee registers
        """
        new_registers = self.get_new_register_values_for_system_call(recorded_system_call, tracee_registers)
        creplayer.set_registers_in_tracee(self.pid, *new_registers.to_list())
        creplayer.run_until_enter_or_exit_of_next_syscall(self.pid)
        self.raise_on_unexpected_return_value(recorded_system_call, self._get_registers_from_tracee())

    def run_tracee_through_system_call(self, recorded_system_call: SystemCall, recorded_system_call_index: int):
        """
        Run a system call for tracee, wrapping/simulating the actual system call the tracee is requesting to do
        with the given recorded system call

        :param recorded_system_call: from original recording
        :param recorded_system_call_index: index of the system call (this is necessary in order to understand if a
        given system call should be simulated or not)
        """
        registers = self._get_registers_from_tracee()
        self.raise_on_unexpected_state(recorded_system_call, registers)
        self.call_stdout_callback_if_relevant(recorded_system_call)
        if should_simulate_system_call(self.system_calls, system_call_index=recorded_system_call_index):
            self.simulate_system_call_for_tracee(recorded_system_call, registers)
        else:
            self.wrap_and_run_real_system_call_in_tracee(recorded_system_call, registers)

    def start_replaying(self) -> int:
        """
        Entry point method to start replaying. Will attach to the process and run it within a sandbox,
        recreating the exact same execution as in the recording.

        :return: tracee exit status
        """
        creplayer.attach_to_tracee_and_begin(self.pid)
        for i, recorded_system_call in enumerate(self.system_calls):
            self.raise_on_tracee_segfault()
            creplayer.run_until_enter_or_exit_of_next_syscall(self.pid)
            self.run_tracee_through_system_call(recorded_system_call, i)
        return self.get_exit_status()


def run_replayer(pid: int, system_calls: List[SystemCall], stdout_callback: Callable):
    """
    Run the sys call interceptor on a given pid with given system calls responses

    :param pid: to run on
    :param system_calls: to give back to process
    :param stdout_callback: to run on any print to stdout (mainly used for testing/debugging purposes)
    """
    return Replayer(pid, system_calls, stdout_callback).start_replaying()


def run_replayer_on_records_at_path(pid: int, path: str, stdout_callback=None):
    """
    Run the sys call interceptor on a given pid with a path to a recording

    :param pid: to run on
    :param path: of recordings
    :param stdout_callback: to run on any print to stdout (mainly used for testing/debugging purposes)
    """
    system_calls = Loader.from_path(path).load_system_calls()
    return run_replayer(pid, system_calls, stdout_callback)
