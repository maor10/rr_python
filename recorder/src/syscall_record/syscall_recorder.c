#include <linux/kernel.h>
#include <linux/unistd.h>
#include <linux/kprobes.h>

#include "utils.h"
#include "record_manager.h"
#include "events_manager.h"
#include "syscall_recorder.h"


/*
 * @purpose:    Record all system calls recorded processes do.
 * 
 * @notes:
 *      - Runs at the beggining of every syscall called on system.
 *      - The pre_syscall function should just record syscall params,
 * 
 *  * @ret: 
 *      1 == run post_syscall after syscall is done
 *      0 == don't run post_syscall after syscall
 */
int pre_syscall(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Record system call done.
 */
int post_syscall(struct kretprobe_instance *probe, struct pt_regs *regs);


struct kretprobe syscall_kretprobe = {
	.kp.symbol_name	= "do_syscall_64",
	.entry_handler 	= pre_syscall,
	.handler		= post_syscall,
	// TODO: Understand why after execve check still need maxactive...
	.maxactive		= 1000
};

int pre_syscall(struct kretprobe_instance * probe, struct pt_regs *regs) {

    struct pt_regs * userspace_regs_ptr = (struct pt_regs *) regs->si;
    struct recorded_event * new_event;
    struct syscall_start_event * new_syscall_start_event;

    IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));

    new_event = create_event(EVENT_ID_SYSCALL_START, current->pid, sizeof(struct syscall_start_event));

    new_syscall_start_event = (struct syscall_start_event *) new_event->event_dump.event;

    memcpy(&(new_syscall_start_event->userspace_regs), userspace_regs_ptr, sizeof(struct pt_regs));

    IF_TRUE_GOTO(add_event(new_event), cleanup_event, "Failed to add rdtsc event!");

    // We don't want to hook the return of execve \ exit because they never return :)
    IF_TRUE_CLEANUP(__NR_execve == regs->di || __NR_exit == regs->di || __NR_exit_group == regs->di);

	return 0;

cleanup_event:
    kfree(new_event);
    return 1;

cleanup:
	return 1;
}

int post_syscall(struct kretprobe_instance *probe, struct pt_regs *regs) {
    return 0;
}

int init_syscalls_record(void) {
    IF_TRUE_CLEANUP(0 > register_kretprobe(&syscall_kretprobe), "Failed to init syscall kprobe!");
    return 0;

cleanup:
    return -1;
}
void unload_syscalls_record(void) {
    unregister_kretprobe(&syscall_kretprobe);
}

int syscalls_start_recording_pid(pid_t pid) {
    return 0;
}

void syscalls_stop_recording_pid(pid_t pid) {
    return;
}
