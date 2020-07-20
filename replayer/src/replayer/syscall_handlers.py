from typing import Dict

from replayer.system_calls import SystemCall

HANDLERS = {}


def syscall_handler(num):
    def _decorator(func):
        HANDLERS[num] = func
        return func
    return _decorator


@syscall_handler(9)
def get_mmap_registers(recorded_system_call: SystemCall, register_values: Dict) -> Dict:
    new_register_values = register_values.copy()
    new_register_values['rdi'] = recorded_system_call.return_value
    new_register_values['r10'] = register_values['r10'] | 0x10
    return new_register_values
