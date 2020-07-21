import pytest

from replayer.system_call_runners.streams import create_streams_from_memory_copies, Stream, \
    BufferWithOffset
from replayer.system_calls.memory_copy import MemoryCopy


def buffer(length):
    return b'a' * length


def memory_copy(to_address, length):
    return MemoryCopy(from_address=0, to_address=to_address, buffer=buffer(length))


@pytest.mark.parametrize('name, starting_addresses, memory_copies, expected_streams', [
    ('simple stream', [1111], [memory_copy(1111, 3)], [
        Stream(
            starting_address=1111,
            buffers_with_offsets=[BufferWithOffset(
                buffer=buffer(3),
                offset=0
            )
            ]
        )
    ]),
    ('multi copies in stream', [1111], [memory_copy(1111, 3), memory_copy(1114, 3)], [
        Stream(
            starting_address=1111,
            buffers_with_offsets=[BufferWithOffset(
                buffer=buffer(3),
                offset=0
            ), BufferWithOffset(
                buffer=buffer(3),
                offset=3
            )
            ]
        )
    ]),
    ('multi copies, multi starting addresses', [1111, 2222], [memory_copy(1111, 3), memory_copy(1114, 3),
                                                              memory_copy(2222, 5)], [
         Stream(
             starting_address=1111,
             buffers_with_offsets=[BufferWithOffset(
                 buffer=buffer(3),
                 offset=0
             ), BufferWithOffset(
                 buffer=buffer(3),
                 offset=3
             )
             ]
         ),
         Stream(
             starting_address=2222,
             buffers_with_offsets=[
                 BufferWithOffset(
                     buffer=buffer(5),
                     offset=0
                 )
             ]
         )
     ]),
    ('simple with offsets', [1111], [memory_copy(1114, 3)], [
        Stream(
            starting_address=1111,
            buffers_with_offsets=[BufferWithOffset(
                buffer=buffer(3),
                offset=3
            )
            ]
        )
    ]),
    ('multi copies, multi starting addresses, offsets', [10, 20, 30], [memory_copy(25, 4), memory_copy(10, 3),
                                                                       memory_copy(16, 5), memory_copy(31, 2)], [
         Stream(
             starting_address=20,
             buffers_with_offsets=[
                 BufferWithOffset(
                     buffer=buffer(4),
                     offset=5
                 )
             ]
         ),
         Stream(
             starting_address=10,
             buffers_with_offsets=[BufferWithOffset(
                 buffer=buffer(3),
                 offset=0
             ), BufferWithOffset(
                 buffer=buffer(5),
                 offset=6
             )
             ]
         ),
         Stream(
             starting_address=30,
             buffers_with_offsets=[
                 BufferWithOffset(
                     buffer=buffer(2),
                     offset=1
                 )
             ]
         )
     ]),
])
def test_create_streams_from_memory_copies(name, starting_addresses, memory_copies, expected_streams):
    streams = create_streams_from_memory_copies(memory_copies=memory_copies,
                                                recorded_starting_addresses_to_replaying_starting_addresses=
                                                {s: s for s in starting_addresses},
                                                )
    assert streams == expected_streams, f'{name} failed'
