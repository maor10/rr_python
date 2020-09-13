from dataclasses import dataclass

@dataclass
class CopyToUser:
    from_addr: int
    to_addr: int
    len: int
    data: bytes