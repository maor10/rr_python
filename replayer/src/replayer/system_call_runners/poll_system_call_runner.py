from _ctypes import sizeof

from replayer.system_call_runners import SystemCallRunner


class PollSystemCallRunner(SystemCallRunner):

    def perform_sys_call(self) -> int:
        pass
