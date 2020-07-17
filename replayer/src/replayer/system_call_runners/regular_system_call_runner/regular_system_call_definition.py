from typing import List, Dict


class RegularSystemCallDefinition:

    def __init__(self, system_call_number: int,  memory_address_registers: List[str] = None):
        self.system_call_number = system_call_number
        self.memory_address_register_names = memory_address_registers or []


REGULAR_SYSTEM_CALL_DEFINITIONS: Dict[int, RegularSystemCallDefinition] = {}


def create_regular_system_call_definition(system_call_number: int,  memory_address_registers: List[str] = None) -> \
        RegularSystemCallDefinition:
    definition = RegularSystemCallDefinition(system_call_number, memory_address_registers)
    REGULAR_SYSTEM_CALL_DEFINITIONS[system_call_number] = definition
    return definition
