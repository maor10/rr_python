from dataclasses import dataclass
from typing import List, Dict

from replayer.system_consts import SYS_CALL_REGISTER, SYS_CALL_NAMES
from .registers import Registers

SYSTEM_CALL_ENTER_EVENT_ID = 1

@dataclass
class SystemCallEnter:

    registers: Registers

    @property
    def num(self) -> int:
        return self.registers.sys_call

    @property
    def name(self) -> int:
        return SYS_CALL_NAMES[self.num]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"
