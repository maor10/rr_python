from typing import Dict

from replayer.loader.system_call import Registers
from replayer.loader.system_call import SystemCall

HANDLERS = {}


def syscall_handler(num):
    def _decorator(func):
        HANDLERS[num] = func
        return func
    return _decorator


@syscall_handler(9)
def get_mmap_registers(recorded_system_call: SystemCall, registers: Registers) -> Registers:
    new_registers = Registers(*registers.to_list())
    new_registers.rdi = recorded_system_call.return_value
    new_registers.r10 = registers.r10 | 0x10
    return new_registers
