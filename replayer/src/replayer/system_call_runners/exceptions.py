

class SyscallException(Exception):
    pass


class NonMatchingSyscallException(SyscallException):

    def __init__(self, expected, requested):
        super(NonMatchingSyscallException, self).__init__(f"Expected {expected}, received {requested}")


class InvalidSyscallException(NonMatchingSyscallException):
    pass


class CouldNotFindStartingAddressForMemoryCopyException(SyscallException):
    pass
