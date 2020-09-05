#include "linux/types.h"
#include "utils.h"


int syscalls_start_recording_pid(pid_t pid) {
    return 0;
}

void syscalls_stop_recording_pid(pid_t pid) {
    return;
}

int init_syscalls_record(void) {
    return 0;
}

void unload_syscalls_record(void) {
    return;
}