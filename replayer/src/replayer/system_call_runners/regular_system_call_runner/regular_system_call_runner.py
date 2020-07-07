from abc import ABCMeta
from replayer.system_call_runners import SystemCallRunner
from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    RegularSystemCallDefinition, REGULAR_SYSTEM_CALL_DEFINITIONS
from .fs_system_call_definitions import *


class RegularSystemCallRunnerMetaclass(ABCMeta):

    def __init__(cls, name, bases, dct):
        super(RegularSystemCallRunnerMetaclass, cls).__init__(name, bases, dct)
        for regular_system_call_definition in REGULAR_SYSTEM_CALL_DEFINITIONS:
            cls.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS[regular_system_call_definition.system_call_number] = cls


class RegularSystemCallRunner(SystemCallRunner, metaclass=RegularSystemCallRunnerMetaclass):

    SYSTEM_CALL_NUMBER = None

    def perform_sys_call(self) -> int:
        system_call_definition: RegularSystemCallDefinition = REGULAR_SYSTEM_CALL_DEFINITIONS[self.system_call_number]
        if system_call_definition.memory_address_register_name is not None:
            buffer_address = self.register_values[system_call_definition.memory_address_register_name]
            self.write_memory_copies_to_address(buffer_address)
        return self.recorded_system_call.return_value
