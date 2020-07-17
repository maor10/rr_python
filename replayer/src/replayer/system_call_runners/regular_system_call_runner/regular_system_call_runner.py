from abc import ABCMeta
from replayer.system_call_runners import SystemCallRunner
from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    RegularSystemCallDefinition, REGULAR_SYSTEM_CALL_DEFINITIONS
from ..streams import create_streams_from_memory_copies
from .system_call_definitions import *


class RegularSystemCallRunnerMetaclass(ABCMeta):

    def __init__(cls, name, bases, dct):
        super(RegularSystemCallRunnerMetaclass, cls).__init__(name, bases, dct)
        for sys_call_number in REGULAR_SYSTEM_CALL_DEFINITIONS:
            cls.SYSTEM_CALL_NUMBERS_TO_SYSTEM_CALL_RUNNERS[sys_call_number] = cls


class RegularSystemCallRunner(SystemCallRunner, metaclass=RegularSystemCallRunnerMetaclass):

    SYSTEM_CALL_NUMBER = None

    def perform_sys_call(self) -> int:
        if self.system_call_number == 47:
            import ipdb; ipdb.set_trace()
        system_call_definition: RegularSystemCallDefinition = REGULAR_SYSTEM_CALL_DEFINITIONS[self.system_call_number]
        recorded_starting_addresses_to_replaying_starting_addresses = {
            self.recorded_system_call.registers[register_name]: self.register_values[register_name]
            for register_name in system_call_definition.memory_address_register_names
        }
        streams = create_streams_from_memory_copies(self.recorded_system_call.memory_copies,
                                                    recorded_starting_addresses_to_replaying_starting_addresses)
        for stream in streams:
            stream.write_memory_copies()

        return self.recorded_system_call.return_value
