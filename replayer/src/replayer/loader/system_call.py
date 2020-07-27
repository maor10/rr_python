from dataclasses import dataclass
from typing import List, Dict

from replayer.system_consts import SYS_CALL_REGISTER, SYS_CALL_NAMES
from .memory_copy import MemoryCopy
from .registers import Registers


@dataclass
class SystemCall:

    registers: Registers
    return_value: int
    memory_copies: List[MemoryCopy]

    @property
    def num(self) -> int:
        return self.registers.sys_call

    @property
    def name(self) -> int:
        return SYS_CALL_NAMES[self.num]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} -> {self.return_value}>"
