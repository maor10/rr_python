from dataclasses import dataclass
from typing import List, Dict

from replayer.system_consts import SYS_CALL_REGISTER
from .memory_copy import MemoryCopy
from replayer.utils import get_syscall_name_from_syscall_num
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
        return get_syscall_name_from_syscall_num(self.num)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} -> {self.return_value}>"
