from dataclasses import dataclass


@dataclass
class MemoryCopy:

    from_address: int
    to_address: int
    buffer: bytes
