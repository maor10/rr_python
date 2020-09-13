#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>


#include "utils.h"
#include "events_manager.h"

#define PROC_NAME "events_dump"

ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos);

struct file_operations proc_ops = {
	.read = read_proc
};

ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos) {
    struct recorded_event *recorded_event = NULL;
    ssize_t ret = 0;

    recorded_event = read_event(0);
    IF_TRUE_CLEANUP(NULL == recorded_event);

    IF_TRUE_GOTO(size < recorded_event->len, error, "Requested read %d too small!", size);
    IF_TRUE_GOTO(0 != copy_to_user(buf, &(recorded_event->event_dump), recorded_event->len), 
                        error,
                        "Failed to copy to user!");

    ret = recorded_event->len;
    goto cleanup;
error:
    ret = -EFAULT;
cleanup:
    if (NULL != recorded_event) {
        // TODO: Document why here you kfree and otherplaces destroy_event
        kfree(recorded_event);
    }

    return ret;
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