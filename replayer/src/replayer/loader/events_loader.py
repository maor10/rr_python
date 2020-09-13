from typing import Dict, List
from .unpacker import BinaryUnpacker
from .rdtsc import RdtscLoader
from .system_call import SystemCallEnterLoader
from .system_call import SystemCallDoneLoader
from .copy_to_user import CopyToUserLoader
from .loader import Loader
from .event import Event

EVENT_TYPE_TO_LOADER = {
    0: RdtscLoader,
    1: SystemCallEnterLoader,
    2: SystemCallDoneLoader,
    3: CopyToUserLoader
}

class EventLoader(Loader):
    def load_single(self):
        pid = self.binary_unpacker.unpack_signed_long()
        event_type = self.binary_unpacker.unpack_unsigned_char()
        
        event_data = EVENT_TYPE_TO_LOADER[event_type](self.binary_unpacker).load_single()
        return Event(pid, event_type, event_data)
