from typing import Dict

from replayer.system_call import SystemCall
from replayer.system_call.loader.consts import REGISTER_NAMES_IN_PROTOCOL_ORDER
from replayer.system_call.memory_copy import MemoryCopy
from replayer.system_call.loader.unpacker import BinaryUnpacker


class Loader:

    def __init__(self, binary_unpacker: BinaryUnpacker):
        self.binary_unpacker = binary_unpacker

    @classmethod
    def from_buffer(cls, buffer: bytes):
        return cls(BinaryUnpacker(buffer))

    @classmethod
    def from_path(cls, path: str):
        with open(path, 'rb') as f:
            return cls.from_buffer(f.read())

    def load_memory_copy(self):
        from_addr = self.binary_unpacker.unpack_unsigned_long()
        to_addr = self.binary_unpacker.unpack_unsigned_long()
        copy_len = self.binary_unpacker.unpack_unsigned_long()
        copy_str = self.binary_unpacker.unpack_str(copy_len)
        return MemoryCopy(
            buffer=copy_str,
            from_address=from_addr,
            to_address=to_addr
        )

    def load_memory_copies(self):
        number_of_copies = self.binary_unpacker.unpack_unsigned_long()
        return [self.load_memory_copy() for _ in range(number_of_copies)]

    def load_register_values(self) -> Dict:
        return {
            register_name: self.binary_unpacker.unpack_unsigned_long()
            for register_name in REGISTER_NAMES_IN_PROTOCOL_ORDER
        }

    def load_system_call(self) -> SystemCall:
        registers = self.load_register_values()
        return_value = self.binary_unpacker.unpack_unsigned_long()
        memory_copies = self.load_memory_copies()
        return SystemCall(
            registers=registers,
            return_value=return_value,
            memory_copies=memory_copies
        )

    def load_system_calls_generator(self):
        while self.binary_unpacker.has_more_bytes():
            yield self.load_system_call()

    def load_system_calls(self):
        return list(self.load_system_calls_generator())
