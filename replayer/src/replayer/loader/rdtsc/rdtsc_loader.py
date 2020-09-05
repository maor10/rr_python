from ..unpacker import BinaryUnpacker
from ..loader import Loader
from .rdtsc import Rdtsc


class RdtscLoader(Loader):
    def load_single(self):
        ax = self.binary_unpacker.unpack_signed_long()
        dx = self.binary_unpacker.unpack_signed_long()
        return Rdtsc(ax=ax, dx=dx)
