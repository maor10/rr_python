from dataclasses import dataclass
from typing import List, Dict

from replayer.consts import SYS_CALL_REGISTER
from replayer.system_calls.memory_copy import MemoryCopy
from replayer.utils import get_syscall_name_from_syscall_num


@dataclass
class SystemCall:

    registers: Dict[str, int]
    return_value: int
    memory_copies: List[MemoryCopy]

    @property
    def num(self) -> int:
        return self.registers[SYS_CALL_REGISTER]

    @property
    def name(self) -> int:
        return get_syscall_name_from_syscall_num(self.num)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} -> {self.return_value}>"
