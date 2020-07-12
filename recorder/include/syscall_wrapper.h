#ifndef SYSCALL_WRAPPER_H
#define SYSCALL_WRAPPER_H

#include <linux/kfifo.h>
#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/wait.h>
#include <linux/sched/signal.h>
#include <linux/types.h>


struct syscall_record {
    pid_t pid;
    struct pt_regs userspace_regs;
    unsigned long ret;

    /* We need to save pointer to userspace regs becuse
     * we need to read userspace eax after syscall to see
     * retcode.
     * 
     * THIS CANNOT BE ACCESS AFTER SYSCALL IS OVER.
     */
    struct pt_regs * userspace_regs_ptr;

    unsigned long amount_of_copies;
    struct list_head current_syscalls;
    
    struct list_head copies_to_user;
};

/*
 * @purpose: Hook syscalls
 */
int init_syscall_hook(void);

/*
 * @purpose: Unhool syscalls
 */
void remove_syscall_hook(void);


/* A var to indicate if *python* code is currently in syscall */
extern struct kfifo recorded_syscalls;

extern struct mutex current_syscalls_mutex;
extern struct list_head current_syscalls;

extern struct mutex recorded_syscalls_mutex;
extern struct wait_queue_head recorded_syscalls_wait;

/*
 * @purpose: Free a syscall record
 */
void free_syscall_record(struct syscall_record *syscall_record);

#endif
