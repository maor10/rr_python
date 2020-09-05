from ..unpacker import BinaryUnpacker
from ..loader import Loader
from .system_call_enter import SystemCallEnter
from .registers import Registers


class SystemCallEnterLoader(Loader):
    def load_single(self):
        registers = Registers(*[self.binary_unpacker.unpack_unsigned_long() for _ in Registers.__annotations__])
        return SystemCallEnter(registers=registers)

