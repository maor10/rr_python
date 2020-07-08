from dataclasses import dataclass
from typing import List, Dict

from replayer.system_call.memory_copy import MemoryCopy


@dataclass
class SystemCall:

    registers: Dict[str, int]
    return_value: int
    memory_copies: List[MemoryCopy]
