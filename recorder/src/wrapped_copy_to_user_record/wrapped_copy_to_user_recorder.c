#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/poll.h>

#include "utils.h"
#include "record_manager.h"
#include "copy_to_user_recorder.h"
#include "events_manager.h"
#include "wrapped_copy_to_user_recorder.h"

struct recorded_mem {
    void __user *ptr;
    unsigned long len;
    unsigned char mem[];
};


/*
 * @purpose: get memory to record before poll syscall
 */
int get_poll_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len);

/*
 * @purpose: get memory to record before getdents syscalls (it calls filldir)
 */
int get_getdents_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len);

/*
 * @purpose: get memory to record before getdents64 syscalls
 */
int get_getdents64_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len);

/*
 * @purpose: Function to be called before wrapped syscall
 */
int pre_copy_wrapper(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Function to be called after wrapped syscall
 */
int post_copy_wrapper(struct kretprobe_instance * probe, struct pt_regs *regs);

DEFINE_WRAPPER(poll_wrapper, "do_sys_poll", get_poll_record_mem);
DEFINE_WRAPPER(getdents_wrapper, "__x64_sys_getdents", get_getdents_record_mem);
DEFINE_WRAPPER(getdents64_wrapper, "ksys_getdents64", get_getdents64_record_mem);

struct kretprobe * copy_wrappers[] = {
    &(poll_wrapper.retprobe),
    &(getdents_wrapper.retprobe),
    &(getdents64_wrapper.retprobe)
};

int get_poll_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len) {
    *addr = (void __user *) regs->di;
    *len = regs->si * sizeof(struct pollfd);

    return 0;
}

int get_getdents_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len) {
    /* For some really fucking weird reason, the regs we get from param here are
        bad, so we take the regsiters from userspace instead... */
    struct pt_regs *userspace_regs = task_pt_regs(current);
    IF_TRUE_CLEANUP(NULL == userspace_regs, "Failed to received userspace regs!");

    *addr = (void __user *) userspace_regs->si;
    *len = userspace_regs->dx;
    
    return 0;
    
cleanup:
    return -1;
}

int get_getdents64_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len) {
    *addr = (void __user *) regs->si;
    *len = regs->dx;

    return 0;
}

int pre_copy_wrapper(struct kretprobe_instance * probe, struct pt_regs *regs) {
    void __user *record_mem;
    unsigned long record_mem_len;
    struct recorded_mem * recorded_mem;
    struct copy_wrapper *copy_wrapper;

    IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));

    copy_wrapper = container_of(probe->rp, struct copy_wrapper, retprobe);

    IF_TRUE_CLEANUP(
        copy_wrapper->get_record_mem_callback(regs, &record_mem, &record_mem_len),
        "Failed to get record memory!"
    );

    recorded_mem = kmalloc(sizeof(struct recorded_mem) + record_mem_len, GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == recorded_mem, "Failed to alloc recorded mem!");
    
    recorded_mem->ptr = record_mem;
    recorded_mem->len = record_mem_len;

    IF_TRUE_GOTO(
        0 != copy_from_user(recorded_mem->mem, record_mem, record_mem_len),
        free_recorded_mem,
        "Failed to copy from user mem!"
    );
    
    memcpy(probe->data, &recorded_mem, sizeof(struct recorded_mem *));

    return 0;

free_recorded_mem:
    kfree(recorded_mem);

cleanup:
    return 1;
}

int post_copy_wrapper(struct kretprobe_instance * probe, struct pt_regs *regs) {
    struct copy_to_user_event *new_event = NULL;
    struct recorded_mem  * recorded_mem = NULL;
    unsigned char * new_mem;
    int i;

    memcpy(&recorded_mem, probe->data, sizeof(struct recorded_mem *));

    new_mem = kmalloc(recorded_mem->len, GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == new_mem, "Failed to alloc new mem!");

    IF_TRUE_CLEANUP(
        0 != copy_from_user(new_mem, recorded_mem->ptr, recorded_mem->len),
        "Failed to copy new mem from user!"
    );

    for (i = 0;i < recorded_mem->len; i++) {
        if (recorded_mem->mem[i] != new_mem[i]) {
            new_event = (struct copy_to_user_event *)create_event(EVENT_ID_COPY_TO_USER, current->pid, sizeof(struct copy_to_user_event) + 1);
            IF_TRUE_CLEANUP(NULL == new_event, "Failed to allocate new event!");

            new_event->from = (void *) NULL;
            new_event->to = recorded_mem->ptr + i;
            new_event->len = 1;
            memcpy(new_event->bytes, new_mem + i, 1);

            IF_TRUE_CLEANUP(add_event(new_event), "Failed to add new wrapped copy event!");
        }
    }

    kfree(recorded_mem);

    return 0;

cleanup:
    if (NULL != recorded_mem) {
        kfree(recorded_mem);
    }

    if (NULL != new_event) {
        destroy_event(new_event);
    }

    return 0;
}

int init_wrapped_copy_to_user_record(void) {
	IF_TRUE_CLEANUP(
        0 > register_kretprobes(copy_wrappers, sizeof(copy_wrappers) / sizeof(struct kretprobe *)),
        "Failed to init copy kprobe!"
    );
    
    return 0;

cleanup:
    return -1;
}

void unload_wrapped_copy_to_user_record(void) {
    unregister_kretprobes(copy_wrappers, sizeof(copy_wrappers) / sizeof(struct kretprobe *));
}

int wrapped_copy_to_user_start_recording_pid(pid_t pid) {
    return 0;
}

void wrapped_copy_to_user_stop_recording_pid(pid_t pid) {
    return;
}
