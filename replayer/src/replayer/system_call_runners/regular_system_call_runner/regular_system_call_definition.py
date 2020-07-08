from typing import List


class RegularSystemCallDefinition:

    def __init__(self, system_call_number: int,  memory_address_register: str = None):
        self.system_call_number = system_call_number
        self.memory_address_register_name = memory_address_register


REGULAR_SYSTEM_CALL_DEFINITIONS: List[RegularSystemCallDefinition] = []


def create_regular_system_call_definition(system_call_number: int,  memory_address_register: str = None):
    REGULAR_SYSTEM_CALL_DEFINITIONS.append(RegularSystemCallDefinition(system_call_number, memory_address_register))
