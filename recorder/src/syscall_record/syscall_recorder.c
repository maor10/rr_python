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
    // Backup pointer to userspace regs to get ret of syscall
    .data_size      = sizeof(struct pt_regs *),
	// TODO: Understand why after execve check still need maxactive...
	.maxactive		= 1000
};

int pre_syscall(struct kretprobe_instance * probe, struct pt_regs *regs) {

    struct pt_regs * userspace_regs_ptr = (struct pt_regs *) regs->si;
    struct syscall_start_event * new_event = NULL;

    IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));

    new_event = create_event(EVENT_ID_SYSCALL_START, current->pid, sizeof(struct syscall_start_event));
    IF_TRUE_CLEANUP(NULL == new_event, "Failed to allocate new event!");

    memcpy(&(new_event->userspace_regs), userspace_regs_ptr, sizeof(struct pt_regs));

    IF_TRUE_GOTO(add_event(new_event), cleanup_event, "Failed to add syscall event!");

    // Backup userspace regs ptr (for later use in post syscall)
    memcpy(probe->data, &userspace_regs_ptr, sizeof(struct pt_regs *));

    // We don't want to hook the return of execve \ exit because they never return :)
    IF_TRUE_CLEANUP(__NR_execve == regs->di || __NR_exit == regs->di || __NR_exit_group == regs->di);

	return 0;

cleanup_event:
    destroy_event(new_event);
    return 1;

cleanup:
	return 1;
}

int post_syscall(struct kretprobe_instance *probe, struct pt_regs *regs) {
    
    struct pt_regs * userspace_regs_ptr;
    struct syscall_done_event * new_event;
    
    new_event = create_event(EVENT_ID_SYSCALL_DONE, current->pid, sizeof(struct syscall_done_event));
    IF_TRUE_CLEANUP(NULL == new_event, "Failed to allocate new event!");

    memcpy(&userspace_regs_ptr, probe->data, sizeof(struct pt_regs *));
    new_event->ret = userspace_regs_ptr->ax;

    IF_TRUE_CLEANUP(add_event(new_event), "Failed to add syscall done event!");

	return 0;

cleanup:
    if (NULL != new_event) {
        destroy_event(new_event);
    }
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
