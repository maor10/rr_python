#include <linux/kprobes.h>
#include <asm/unistd.h>
#include <linux/mutex.h>

#include "syscall_wrapper.h"
#include "copy_to_user_wrapper.h"
#include "utils.h"

// TODO -- is 1 << 15 Too big???
// Maybe we should just save pointer to heap in kfifo?
#define SYSCALL_FIFO_ORDER (15)
#define SYSCALL_FIFO_SIZE (1 << SYSCALL_FIFO_ORDER)

/*
 * @purpose:    Record all system calls recorded processes do.
 * 
 * @notes:
 *      - Runs at the beggining of every syscall called on system.
 *      - The pre_syscall function should just record syscall params,
 *          only on post_syscall we record entire syscall (only then we
 *          have the return value of syscall)
 * 
 *  * @ret: 
 *      1 == run post_syscall after syscall is done
 *      0 == don't run post_syscall after syscall
 */
int pre_syscall(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Runs AFTER selected syscalls where run - and records entire syscall
 *              (with return values)
 */
int post_syscall(struct kretprobe_instance *probe, struct pt_regs *regs);

DEFINE_MUTEX(current_syscalls_mutex);
LIST_HEAD(current_syscalls);

DEFINE_MUTEX(recorded_syscalls_mutex);
struct kfifo recorded_syscalls;
DECLARE_WAIT_QUEUE_HEAD(recorded_syscalls_wait);

struct kretprobe syscall_kretprobe = {
	.kp.symbol_name	= "do_syscall_64",
	.entry_handler 	= pre_syscall,
	.handler		= post_syscall,
	// TODO: Understand why after execve check still need maxactive...
	.maxactive		= 1000,
    .data_size = sizeof(struct syscall_record *)

};

void free_syscall_record(struct syscall_record *syscall_record)
{
    struct copy_record_element *copy_record_element;
    struct copy_record_element *tmp_record_element;

    list_for_each_entry_safe(copy_record_element, tmp_record_element, &(syscall_record->copies_to_user), list) {
        free_copy_record(copy_record_element);
    }

    kfree(syscall_record);
}

int pre_syscall(struct kretprobe_instance * probe, struct pt_regs *regs) {

    struct pt_regs * userspace_regs_ptr = (struct pt_regs *) regs->si;
    struct syscall_record * current_syscall;

    // We don't want to hook the return of execve \ exit because they never return :)
    IF_TRUE_CLEANUP(__NR_execve == regs->di || __NR_exit == regs->di || __NR_exit_group == regs->di);
    
	// TODO: RECORD ONLY SPECIFIC PROCESSES
	IF_TRUE_CLEANUP(0 != strcmp(current->comm, "python"));
    
    current_syscall = kmalloc(sizeof(struct syscall_record), GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == current_syscall, "Failed to alloc syscall record!");

    // Init current syscall record
    current_syscall->amount_of_copies = 0;
    INIT_LIST_HEAD(&(current_syscall->copies_to_user));

    memcpy(&(current_syscall->userspace_regs), userspace_regs_ptr, sizeof(struct pt_regs));
    current_syscall->userspace_regs_ptr = userspace_regs_ptr;
    current_syscall->pid = current->pid;
    
    // TODO CHANGE TO RCU LOCK!
    mutex_lock(&current_syscalls_mutex);
    list_add(&current_syscall->current_syscalls, current_syscalls);
    mutex_unlock(&current_syscalls_mutex);

    memcpy(probe->data, current_syscall, sizeof(struct syscall_record * ));

	return 0;

cleanup:
	return 1;
}

int post_syscall(struct kretprobe_instance *probe, struct pt_regs *regs) {

    struct syscall_record * current_syscall;
    unsigned int kfifo_ret;

    memcpy(current_syscall, probe->data, sizeof(struct syscall_record *));

    current_syscall->ret = current_syscall->userspace_regs_ptr->ax;

    mutex_lock(&recorded_syscalls_mutex);
    kfifo_ret = kfifo_in(&recorded_syscalls, &current_syscall, sizeof(void *));
    mutex_unlock(&recorded_syscalls_mutex);

    IF_TRUE_GOTO(sizeof(void *) == kfifo_ret, free_syscall, "Failed to insert to kfifo!");
    wake_up(&recorded_syscalls_wait);

    goto cleanup;

free_syscall:
    free_syscall_record(current_syscall);

cleanup:
    mutex_lock(&current_syscalls_mutex);
    list_del(&current_syscall->current_syscalls);
    mutex_unlock(&current_syscalls_mutex);

	return 0;
}

int init_syscall_hook(void) {

    IF_TRUE_GOTO(kfifo_alloc(&recorded_syscalls, SYSCALL_FIFO_SIZE, GFP_KERNEL),
                    cleanup_unregister_kprobe, "Failed to alloc kfifo!");

	IF_TRUE_CLEANUP(0 > register_kretprobe(&syscall_kretprobe), "Failed to init syscall kprobe!");
    return 0;

cleanup_unregister_kprobe:
    unregister_kretprobe(&syscall_kretprobe);

cleanup:
    return -1;
}

void remove_syscall_hook(void) {
    unregister_kretprobe(&syscall_kretprobe);
    kfifo_free(&recorded_syscalls);
}