from typing import List, Callable
import creplayer
from replayer import syscall_handlers, system_consts
from replayer.system_consts import REGISTER_NAMES, SYS_CALL_REGISTER, SYS_CALL_NAMES, EXIT_GROUP_SYS_CALL, \
    WRITE_SYS_CALL
from replayer.exceptions import NoSuchSysCallRunnerExistsException, NoSysCallsLeftException, UnexpectedSysCallException
from replayer.should_simulate import should_simulate_system_call
from replayer.system_calls import SystemCall
from replayer.system_calls.loader.system_call_loader import Loader
from replayer.system_call_runners import SystemCallRunner, RegularSystemCallRunner


class Replayer:

    def __init__(self, pid: int, system_calls: List[SystemCall], stdout_callback=None):
        self.pid = pid
        self.system_calls = system_calls
        self.stdout_callback = stdout_callback

    @classmethod
    def from_pid_and_system_calls(cls, pid: int, system_calls: List[SystemCall], stdout_callback=None):
        return cls(pid, system_calls, stdout_callback)

    def ran_syscall_result_callback(self, sys_call_index: int, syscall_result: int):
        system_call = self.system_calls[sys_call_index]
        if should_simulate_system_call(self.system_calls, sys_call_index):
            raise Exception("Should not have gotten here")
        expected_return_value = system_call.return_value
        if syscall_result != expected_return_value:
            if system_call.num not in [3, 41, 257]:
                raise Exception(f"Unexpected syscall result {syscall_result}, expected {expected_return_value}")

    def has_supported_syscall_runner_for_system_call(self, sys_call_index: int, sys_call_number: int, *registers) -> bool:
        """
        Callback for a booleanic question of whether a sys call number at a syscall index is supported

        :param sys_call_index: at what index should the sys call number be checked if supported
        :param sys_call_number: to check if supported
        :return: whether or not it's supported

        :raises UnexpectedSysCallException if a request for a sys call came that was out of context
        """
        # we did not hit this in record and do hit this in replay; probably has to do with ptrace
        # TODO figure out if we need this
        if sys_call_number == EXIT_GROUP_SYS_CALL:
            return False

        if sys_call_index >= len(self.system_calls):
            raise NoSysCallsLeftException()

        system_call = self.system_calls[sys_call_index]
        register_values = self._get_register_values(registers)

        if system_call.num != sys_call_number:
            print(f"{sys_call_index} / {len(self.system_calls)}")
            raise UnexpectedSysCallException(expected=system_call.num,
                                             received=sys_call_number)

        if sys_call_number not in [0, 3, 5, 9, 10]:
            for k, v in register_values.items():
                assert system_call.registers[k] == v, f"(In {system_call.name}) Unexpected for {k}, expected {system_call.registers[k]} got {v}"

        return should_simulate_system_call(self.system_calls, system_call_index=sys_call_index)

    def get_register_values_before_syscall_callback(self, syscall_index, syscall_number, *registers):
        if syscall_number == EXIT_GROUP_SYS_CALL:
            return registers
        register_values = self._get_register_values(registers)
        recorded_system_call = self.system_calls[syscall_index]
        handler = syscall_handlers.HANDLERS.get(syscall_number)
        new_register_values = handler(recorded_system_call, register_values) if handler else register_values
        return tuple(new_register_values.values())

    def simulate_system_call_handler(self, sys_call_index: int, sys_call_number: int = None, *registers) -> int:
        """
        Handles simulation of a given system call made by the replayed process
        Only system calls that passed has_supported_... should be simulated with this handler

        :param sys_call_index: system call index (# of syscall)
        :param sys_call_number: to simulate
        :param registers: the current registers of the replayed process
        :return: system call result
        """
        if sys_call_index >= len(self.system_calls):
            raise NoSysCallsLeftException()

        current_register_values = self._get_register_values(registers)
        system_call = self.system_calls[sys_call_index]

        # rdi 1 is fd stdout
        if system_call.num == system_consts.WRITE_SYS_CALL and system_call.registers['rdi'] == 1 \
                and self.stdout_callback is not None:
            self.stdout_callback(creplayer.get_memory_from_replayed_process(system_call.registers['rsi'],
                                                                            system_call.registers['rdx']))

        system_call_runner = RegularSystemCallRunner(sys_call_number, current_register_values, system_call)
        return system_call_runner.run()

    def start_replaying(self):
        return creplayer.start_replay_with_pid_and_handlers(self.pid,
                                                            self.get_register_values_before_syscall_callback,
                                                            self.has_supported_syscall_runner_for_system_call,
                                                            self.ran_syscall_result_callback,
                                                            self.simulate_system_call_handler)

    @staticmethod
    def _get_register_values(registers):
        return {
            register_name: register
            for (register_name, register) in zip(REGISTER_NAMES, registers)
        }


def run_replayer(pid: int, system_calls: List[SystemCall], stdout_callback: Callable):
    """
    Run the sys call interceptor on a given pid with given system calls responses

    :param pid: to run on
    :param system_calls: to give back to process
    :param stdout_callback: to run on any print to stdout (mainly used for testing/debugging purposes)
    """
    return Replayer.from_pid_and_system_calls(pid, system_calls, stdout_callback).start_replaying()


def run_replayer_on_records_at_path(pid: int, path: str, stdout_callback=None):
    system_calls = Loader.from_path(path).load_system_calls()
    return run_replayer(pid, system_calls, stdout_callback)
