from abc import ABCMeta, abstractmethod
from typing import Dict, Type, List, Tuple

from replayer.system_calls import SystemCall
import creplayer
from replayer.system_call_runners.exceptions import InvalidSyscallException


class SystemCallRunner(metaclass=ABCMeta):

    SYSTEM_CALL_NUMBER: int = NotImplementedError

    SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS: Dict[int, Type['SystemCallRunner']] = {}

    def __init__(self, sys_call_number, register_values: Dict[str, int], recorded_system_call: SystemCall):
        self.system_call_number = sys_call_number
        self.register_values = register_values
        self.recorded_system_call = recorded_system_call

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS[cls.SYSTEM_CALL_NUMBER] = cls

    @abstractmethod
    def perform_sys_call(self) -> int:
        pass

    def run(self) -> int:
        if self.system_call_number != self.recorded_system_call.registers['orig_ax']:
            raise InvalidSyscallException(expected=self.recorded_system_call.registers['orig_ax'],
                                          requested=self.system_call_number)
        return self.perform_sys_call()
