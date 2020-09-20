from dataclasses import dataclass

SYSTEM_CALL_DONE_EVENT_ID = 2

@dataclass
class SystemCallDone:

    ret: int

    def __repr__(self):
        return f"<{self.__class__.__name__} Ret: {self.ret}>"
