from replayer.system_consts import SYS_CALL_NAMES


def get_syscall_name_from_syscall_num(syscall_num: int):
    return SYS_CALL_NAMES[syscall_num]
