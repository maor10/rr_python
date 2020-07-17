from _ctypes import sizeof

from replayer.system_call_runners import SystemCallRunner
from replayer.system_call_runners.streams import create_streams_from_memory_copies


class IoctlSystemCallRunner(SystemCallRunner):

    SYSTEM_CALL_NUMBER = 16

    def perform_sys_call(self) -> int:
        print(f"Got ioctl number {self.recorded_system_call.registers['rsi']}")
        if self.recorded_system_call.registers['rsi'] == 21531:
            # import ipdb; ipdb.set_trace()
            # import time; time.sleep(10)
            print(f"IOCTL 21531 {self.recorded_system_call.memory_copies} copies")
            streams = create_streams_from_memory_copies(self.recorded_system_call.memory_copies,
                                                        {
                                                            self.recorded_system_call.registers['rdx']: self.register_values['rdx']
                                                        })
            for stream in streams:
                stream.write_memory_copies()
        else:
            if len(self.recorded_system_call.memory_copies) > 0:
                raise Exception("iiiii")
        return self.recorded_system_call.num
