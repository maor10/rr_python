#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>

#include "utils.h"
#include "recording_control_procfile.h"
#include "record_manager.h"

#define PROC_NAME "record_command"

#define START_RECORD_ME (1)
#define STOP_RECORD_ME  (0)

struct proc_dir_entry * recorded_processes_proc_ent = NULL;

/*
 * @purpose: file operation to run when /proc/recorded_process is written to.
 */
ssize_t write_proc(struct file *file, const char __user *ubuf, size_t count, loff_t *ppos);


struct file_operations recorded_processes_proc_ops = {
	.write = write_proc,
};


ssize_t write_proc(struct file *file, const char __user *ubuf, size_t count, loff_t *ppos) {
    int command;

	IF_TRUE_CLEANUP(kstrtoint_from_user(ubuf, count, 10, &command));
    LOG("Received command %d", command);

    switch (command)
    {
    case START_RECORD_ME:
        IF_TRUE_CLEANUP(start_recording_pid(current->pid), "Failed to start recording pid");
        break;
    
    case STOP_RECORD_ME:
        IF_TRUE_CLEANUP(stop_recording_pid(current->pid), "Failed to stop recording pid!");
        break;

    default:
        goto cleanup;
        break;
    }

	return count;
cleanup:
    return -EFAULT;
}


int init_recording_control_procfile(void) {
    recorded_processes_proc_ent = proc_create(PROC_NAME, 0666, NULL, &recorded_processes_proc_ops);
    IF_TRUE_CLEANUP(NULL == recorded_processes_proc_ent, "Failed to create proc entry!");

    return 0;
cleanup:
    return -1;
}


void unload_recording_control_procfile(void) {
    remove_proc_entry(PROC_NAME, NULL);
}