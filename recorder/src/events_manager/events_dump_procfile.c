#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/sched/signal.h>



#include "utils.h"
#include "events_manager.h"

#define PROC_NAME "events_dump"

/*
 * @purpose: func called when read from the events proc file /proc/<PROC_NAME> 
 */
ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos);

struct file_operations proc_ops = {
	.read = read_proc
};

ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos) {
    ssize_t ret;

    DEFINE_WAIT(wait);

    add_wait_queue(&recorded_events_wait, &wait);

    while (is_events_empty()) {
        IF_TRUE_GOTO(file->f_flags & O_NONBLOCK, cleanup_noblock);

        prepare_to_wait(&recorded_events_wait, &wait, TASK_INTERRUPTIBLE);
        schedule();

        // TODO Make sure we did dis good
        // If woken up from signal
        IF_TRUE_GOTO(signal_pending(current), cleanup_signal);

    }
    
    ret = dump_events(buf, size);
    goto cleanup;

cleanup_signal:
    ret = -ERESTARTSYS;
    goto cleanup;

cleanup_noblock:
    ret = 0;

cleanup:
    finish_wait(&recorded_events_wait, &wait);
    return ret;
//    return dump_events(buf, size);
}

int init_events_dump_procfile(void) {
    IF_TRUE_CLEANUP(NULL == proc_create(PROC_NAME, 0666, NULL, &proc_ops),
                        "Failed to init dump procfile");

    return 0;
cleanup:
    return -1;
}

void unload_events_dump_procfile(void) {
    remove_proc_entry(PROC_NAME, NULL);
}