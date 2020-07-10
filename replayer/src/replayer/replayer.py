from typing import List
import creplayer
from replayer.consts import REGISTER_NAMES, SYS_CALL_REGISTER, SYS_CALL_NAMES
from replayer.exceptions import NoSuchSysCallRunnerExistsException
from replayer.system_call import SystemCall
from replayer.system_call.loader.loader import Loader
from replayer.system_call_runners import SystemCallRunner


class Replayer:

    def __init__(self, pid: int, system_calls: List[SystemCall]):
        self.pid = pid
        self.system_calls = system_calls

    @classmethod
    def from_pid_and_system_calls(cls, pid: int, system_calls: List[SystemCall]):
        system_calls = [system_call for system_call in system_calls
                        if cls.has_supported_syscall_runner_for_system_call(system_call.registers[SYS_CALL_REGISTER])]
        return cls(pid, system_calls)

    @staticmethod
    def has_supported_syscall_runner_for_system_call(sys_call_number):
        will_run = sys_call_number in SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS
        return will_run

    def system_call_handler(self, sys_call_number: int = None, *registers):
        if len(self.system_calls) == 0:
            raise NoSuchSysCallRunnerExistsException()
        current_register_values = self._get_register_values(registers)
        recorded_system_call = self.system_calls.pop(0)
        system_call_runner_cls = SystemCallRunner.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS[sys_call_number]
        if system_call_runner_cls is None:
            raise NoSuchSysCallRunnerExistsException(sys_call_number)
        system_call_runner = system_call_runner_cls(sys_call_number, current_register_values, recorded_system_call)
        return system_call_runner.run()

    def start_replaying(self):
        creplayer.start_replay_with_pid_and_handlers(self.pid,
                                                     self.has_supported_syscall_runner_for_system_call,
                                                     self.system_call_handler)

    @staticmethod
    def _get_register_values(registers):
        return {
            register_name: register
            for (register_name, register) in zip(REGISTER_NAMES, registers)
        }


def run_replayer(pid: int, system_calls: List[SystemCall]):
    """
    Run the sys call interceptor on a given pid with given system calls responses

    :param pid: to run on
    :param system_calls: to give back to process
    """
    Replayer.from_pid_and_system_calls(pid, system_calls).start_replaying()


def run_replayer_on_records_at_path(pid: int, path: str):
    system_calls = Loader.from_path(path).load_system_calls()
    Replayer.from_pid_and_system_calls(pid, system_calls).start_replaying()
