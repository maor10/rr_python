from abc import ABCMeta
from replayer.system_call_runners import SystemCallRunner
from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    RegularSystemCallDefinition, REGULAR_SYSTEM_CALL_DEFINITIONS
from ..streams import create_streams_from_memory_copies
from .system_call_definitions import *
import creplayer


class RegularSystemCallRunner(SystemCallRunner):

    def perform_sys_call(self) -> int:
        # system_call_definition: RegularSystemCallDefinition = REGULAR_SYSTEM_CALL_DEFINITIONS[self.system_call_number]
        # recorded_starting_addresses_to_replaying_starting_addresses = {
        #     self.recorded_system_call.registers[register_name]: self.register_values[register_name]
        #     for register_name in system_call_definition.memory_address_register_names
        # }
        # streams = create_streams_from_memory_copies(self.recorded_system_call.memory_copies,
        #                                             recorded_starting_addresses_to_replaying_starting_addresses)
        # for stream in streams:
        #     stream.write_memory_copies()
        for memory_copy in self.recorded_system_call.memory_copies:
            creplayer.set_memory_in_replayed_process(memory_copy.to_address,
                                                     memory_copy.buffer)
        return self.recorded_system_call.return_value


