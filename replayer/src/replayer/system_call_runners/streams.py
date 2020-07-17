from dataclasses import dataclass
from typing import List, Dict
import creplayer
from replayer.system_calls.memory_copy import MemoryCopy
from replayer.system_call_runners.exceptions import CouldNotFindStartingAddressForMemoryCopyException


@dataclass
class BufferWithOffset:

    buffer: bytes
    offset: int


class Stream:

    def __init__(self, starting_address, buffers_with_offsets: List[BufferWithOffset]):
        self.starting_address = starting_address
        self.buffers_with_offsets = buffers_with_offsets

    def __eq__(self, other: 'Stream'):
        return self.buffers_with_offsets == other.buffers_with_offsets

    def __repr__(self):
        return f"<{self.__class__.__name__} at {self.starting_address}>"

    def write_memory_copies(self):
        for buffer_with_offset in self.buffers_with_offsets:
            creplayer.set_memory_in_replayed_process(self.starting_address + buffer_with_offset.offset,
                                                     buffer_with_offset.buffer)


def get_closest_starting_address(memory_copy: MemoryCopy, starting_addresses: List[int]):
    relevant_starting_addresses = [starting_address for starting_address in starting_addresses
                                   if memory_copy.to_address >= starting_address]
    if len(relevant_starting_addresses) == 0:
        raise CouldNotFindStartingAddressForMemoryCopyException()
    return max(relevant_starting_addresses)


def create_streams_from_memory_copies(memory_copies: List[MemoryCopy],
                                      recorded_starting_addresses_to_replaying_starting_addresses: Dict[int, int]) \
        -> List[Stream]:
    """
    Splits memory copies into a list of streams- each stream represents a single copy operation which was chunked into
    different memory copies (e.g if there was a big copy that was done in two steps, then the "big copy" would be the
    stream, which would contain the "two steps" which would be the memory copies)

    :param memory_copies: to chunk into streams
    :param recorded_starting_addresses_to_replaying_starting_addresses: where streams should begin
    :return: list of streams
    """
    starting_addresses_to_memory_copies_with_offsets = {}
    for memory_copy in memory_copies:
        recorded_starting_addresses = list(recorded_starting_addresses_to_replaying_starting_addresses.keys())
        recorded_starting_address = get_closest_starting_address(memory_copy, recorded_starting_addresses)
        memory_copy_with_offset = BufferWithOffset(
            buffer=memory_copy.buffer,
            offset=memory_copy.to_address - recorded_starting_address
        )
        replaying_starting_address = \
            recorded_starting_addresses_to_replaying_starting_addresses[recorded_starting_address]
        starting_addresses_to_memory_copies_with_offsets.setdefault(replaying_starting_address, []).append(
            memory_copy_with_offset
        )
    return [Stream(starting_address=starting_address, buffers_with_offsets=buffers_with_offsets)
            for starting_address, buffers_with_offsets in starting_addresses_to_memory_copies_with_offsets.items()]
