from abc import ABCMeta, abstractmethod
from typing import Dict, Type, List, Tuple

from replayer.system_call import SystemCall
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

    def write_memory_copies_to_address(self, address: int, number_of_copies: int = None):
        number_of_copies = number_of_copies or len(self.recorded_system_call.memory_copies)
        for _ in range(number_of_copies):
            memory_copy = self.recorded_system_call.memory_copies.pop(0)
            creplayer.set_memory_in_replayed_process(address,
                                                     memory_copy.buffer)
            address += len(memory_copy.buffer)

    @abstractmethod
    def perform_sys_call(self) -> int:
        pass

    def run(self) -> int:
        if self.system_call_number != self.recorded_system_call.registers['orig_ax']:
            raise InvalidSyscallException()
        return self.perform_sys_call()
