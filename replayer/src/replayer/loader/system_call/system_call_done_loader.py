from ..loader import Loader
from .system_call_done import SystemCallDone


class SystemCallDoneLoader(Loader):
    def load_single(self):
        ret = self.binary_unpacker.unpack_unsigned_long()
        return SystemCallDone(ret=ret)

