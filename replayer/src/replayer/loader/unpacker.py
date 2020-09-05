import struct


class BinaryUnpacker:

    UNSIGNED_LONG_SIZE = 8  # in bytes
    UNSIGNED_CHAR_SIZE = 1  # in bytes

    def __init__(self, buffer: bytes):
        self.buffer = buffer

    def unpack_unsigned_char(self):
        ret = struct.unpack("<B", self.buffer[:self.UNSIGNED_CHAR_SIZE])[0]
        self.buffer = self.buffer[self.UNSIGNED_CHAR_SIZE:]

        return ret

    def unpack_unsigned_long(self):
        ret = struct.unpack("<Q", self.buffer[:self.UNSIGNED_LONG_SIZE])[0]
        self.buffer = self.buffer[self.UNSIGNED_LONG_SIZE:]

        return ret

    def unpack_signed_long(self):
        ret = struct.unpack("<q", self.buffer[:self.UNSIGNED_LONG_SIZE])[0]
        self.buffer = self.buffer[self.UNSIGNED_LONG_SIZE:]
        return ret

    def unpack_str(self, str_len):
        ret = self.buffer[:str_len]
        self.buffer = self.buffer[str_len:]

        return ret

    def has_more_bytes(self):
        return 0 != len(self.buffer)
