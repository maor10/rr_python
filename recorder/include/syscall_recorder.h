#ifndef SYSCALL_RECORDER_H
#define SYSCALL_RECORDER_H

#include <linux/types.h>
#include <linux/kernel.h>
#include <asm/ptrace.h>

struct syscall_start_event {
    struct pt_regs userspace_regs;
};

int init_syscalls_record(void);
void unload_syscalls_record(void);

int syscalls_start_recording_pid(pid_t pid);
void syscalls_stop_recording_pid(pid_t pid);

#endif