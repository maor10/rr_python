from typing import Dict, List
from .unpacker import BinaryUnpacker
from .rdtsc import RdtscLoader, RDTSC_EVENT_ID
from .system_call import SystemCallEnterLoader, SystemCallDoneLoader, SYSTEM_CALL_ENTER_EVENT_ID, SYSTEM_CALL_DONE_EVENT_ID
from .copy_to_user import CopyToUserLoader, COPY_TO_USER_EVENT_ID
from .loader import Loader
from .event import Event

EVENT_TYPE_TO_LOADER = {
    RDTSC_EVENT_ID:             RdtscLoader,
    SYSTEM_CALL_ENTER_EVENT_ID: SystemCallEnterLoader,
    SYSTEM_CALL_DONE_EVENT_ID:  SystemCallDoneLoader,
    COPY_TO_USER_EVENT_ID:      CopyToUserLoader
}

class EventLoader(Loader):
    def load_single(self):
        pid = self.binary_unpacker.unpack_signed_long()
        event_type = self.binary_unpacker.unpack_unsigned_char()
        
        event_data = EVENT_TYPE_TO_LOADER[event_type](self.binary_unpacker).load_single()
        return Event(pid, event_type, event_data)
