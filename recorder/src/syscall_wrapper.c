#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/poll.h>

#include "utils.h"
#include "copy_to_user_wrapper.h"
#include "syscall_recorder.h"
#include "recorded_processes_loader.h"


// See docs for explenation
struct syscall_wrapper {
    int (*get_record_mem_callback) (struct pt_regs *, void * __user *, unsigned long *);
    struct kretprobe retprobe;
};

struct syscall_recorded_mem {
    void __user *ptr;
    unsigned long len;
    unsigned char mem[];
};

/*
 * @purpose: get memory to record before poll syscall
 */
int get_poll_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len);

/*
 * @purpose: Function to be called before wrapped syscall
 */
int pre_wrap_syscall(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Function to be called after wrapped syscall
 */
int post_wrap_syscall(struct kretprobe_instance * probe, struct pt_regs *regs);

struct syscall_wrapper poll_wrapper = {
    .get_record_mem_callback    = get_poll_record_mem,
    .retprobe.kp.symbol_name	= "do_sys_poll",
    .retprobe.entry_handler 	= pre_wrap_syscall,
    .retprobe.handler		    = post_wrap_syscall,
    .retprobe.maxactive	    	= 1000,
    .retprobe.data_size	    	= sizeof(struct poll_recorded_mem *),
};

struct kretprobe * syscall_wrappers[] = {
    &(poll_wrapper.retprobe)
};

int get_poll_record_mem(struct pt_regs * regs, void * __user *addr, unsigned long *len) {
    *addr = (void __user *) regs->di;
    *len = regs->si * sizeof(struct pollfd);

    return 0;
}

int pre_wrap_syscall(struct kretprobe_instance * probe, struct pt_regs *regs) {
    void __user *record_mem;
    unsigned long record_mem_len;
    struct syscall_recorded_mem * recorded_mem;
    struct syscall_wrapper *syscall_wrapper;

    IF_TRUE_CLEANUP(current->pid != recorded_process_pid || recorded_process_pid == 0);
    IF_TRUE_CLEANUP(NULL == current_syscall_record);

    syscall_wrapper = container_of(probe->rp, struct syscall_wrapper, retprobe);

    IF_TRUE_CLEANUP(
        syscall_wrapper->get_record_mem_callback(regs, &record_mem, &record_mem_len),
        "Failed to get record memory!"
    );

    recorded_mem = kmalloc(sizeof(struct syscall_recorded_mem) + record_mem_len, GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == recorded_mem, "Failed to alloc recorded mem!");
    
    recorded_mem->ptr = record_mem;
    recorded_mem->len = record_mem_len;

    IF_TRUE_GOTO(
        0 != copy_from_user(recorded_mem->mem, record_mem, record_mem_len),
        free_recorded_mem,
        "Failed to copy from user mem!"
    );
    
    memcpy(probe->data, &recorded_mem, sizeof(struct syscall_recorded_mem *));

    return 0;

free_recorded_mem:
    kfree(recorded_mem);

cleanup:
    return 1;
}

int post_wrap_syscall(struct kretprobe_instance * probe, struct pt_regs *regs) {
    struct syscall_recorded_mem * recorded_mem;
    unsigned char * new_mem;
    int i;
    struct copy_record_element * current_copy;

    memcpy(&recorded_mem, probe->data, sizeof(struct syscall_recorded_mem *));

    new_mem = kmalloc(recorded_mem->len, GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == new_mem, "Failed to alloc new mem!");

    IF_TRUE_GOTO(
        0 != copy_from_user(new_mem, recorded_mem->ptr, recorded_mem->len),
        cleanup_new_mem,
        "Failed to copy new mem from user!"
    );

    for (i = 0;i < recorded_mem->len; i++) {
        if (recorded_mem->mem[i] != new_mem[i]) {
            current_copy = kmalloc(sizeof(struct copy_record_element) + 1, GFP_KERNEL);
            IF_TRUE_GOTO(NULL == current_copy, cleanup_new_mem, "Failed to alloc current 1 byte copy!");

            current_copy->record.from = (void *) NULL;
            current_copy->record.to = recorded_mem->ptr + i;
            current_copy->record.len = 1;
            memcpy(current_copy->record.bytes, new_mem + i, 1);
            list_add_tail(&current_copy->list, &(current_syscall_record->copies_to_user));
            current_syscall_record->amount_of_copies++;
        }
    }

cleanup_new_mem:
    kfree(new_mem);
cleanup:
    kfree(recorded_mem);

    return 0;
}

int init_syscall_wrappers(void) {
    IF_TRUE_CLEANUP(
        0 > register_kretprobes(syscall_wrappers, sizeof(syscall_wrappers) / sizeof(struct kretprobe *)),
        "Failed to init copy kprobe!"
    );

    return 0;
}

int init_syscall_wrappers(void) {
    IF_TRUE_CLEANUP(
        0 > register_kretprobes(syscall_wrappers, sizeof(syscall_wrappers) / sizeof(struct kretprobe *)),
        "Failed to init copy kprobe!"
    );

cleanup:
    return -1;
}

void remove_syscall_wrappers(void) {
    unregister_kretprobes(syscall_wrappers, sizeof(syscall_wrappers) / sizeof(struct kretprobe *));
}