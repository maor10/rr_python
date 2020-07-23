

class TracingException(Exception):
    pass


class TraceeException(Exception):
    pass


class SegfaultException(TraceeException):
    pass
