

class ReplayerException(Exception):
    pass


class NoSuchSysCallRunnerExistsException(ReplayerException):
    pass


class NoSysCallsLeftException(ReplayerException):
    pass
