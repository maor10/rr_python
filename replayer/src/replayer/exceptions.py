from .system_consts import SYS_CALL_NAMES


class ReplayerException(Exception):
    pass


class NoSuchSysCallRunnerExistsException(ReplayerException):
    pass


class NoSysCallsLeftException(ReplayerException):
    pass


class UnexpectedSysCallException(ReplayerException):

    def __init__(self, expected: int, received: int):
        super(UnexpectedSysCallException, self).__init__(f"Expected {SYS_CALL_NAMES[expected]}, got "
                                                         f"{SYS_CALL_NAMES[received]}")
