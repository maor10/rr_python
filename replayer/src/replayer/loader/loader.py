from abc import ABC, abstractmethod

from .unpacker import BinaryUnpacker

class Loader(ABC):
    def __init__(self, binary_unpacker: BinaryUnpacker):
        self.binary_unpacker = binary_unpacker

    @classmethod
    def from_buffer(cls, buffer: bytes):
        return cls(BinaryUnpacker(buffer))

    @classmethod
    def from_path(cls, path: str):
        with open(path, 'rb') as f:
            return cls.from_buffer(f.read())

    @abstractmethod
    def load_single(self):
        pass

    def load_many_generator(self):
        while self.binary_unpacker.has_more_bytes():
            yield self.load_single()

    def load_many(self):
        return list(self.load_many_generator())
