from ..unpacker import BinaryUnpacker
from ..loader import Loader
from .copy_to_user import CopyToUser


class CopyToUserLoader(Loader):
    def load_single(self):
        from_addr = self.binary_unpacker.unpack_signed_long()
        to_addr = self.binary_unpacker.unpack_signed_long()
        len = self.binary_unpacker.unpack_signed_long()
        data = self.binary_unpacker.unpack_str(len)

        return CopyToUser(from_addr=from_addr, to_addr=to_addr, len=len, data=data)
