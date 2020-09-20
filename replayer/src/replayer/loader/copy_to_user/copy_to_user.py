from dataclasses import dataclass

COPY_TO_USER_EVENT_ID = 3

@dataclass
class CopyToUser:
    from_addr: int
    to_addr: int
    len: int
    data: bytes