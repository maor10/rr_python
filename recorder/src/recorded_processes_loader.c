#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/prctl.h>

#include <linux/kallsyms.h>


#include "utils.h"
#include "recorded_processes_loader.h"


#define PROC_NAME "record_command"

#define START_RECORD_ME (1)
#define STOP_RECORD_ME  (0)

int (*my_set_tsc_mode)(unsigned int val);

struct proc_dir_entry * recorded_processes_proc_ent = NULL;

int recorded_process_pid = 0;


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
        recorded_process_pid = current->pid;
        my_set_tsc_mode(PR_TSC_SIGSEGV);
        break;
    
    case STOP_RECORD_ME:
        my_set_tsc_mode(PR_TSC_ENABLE);
        recorded_process_pid = 0;
        break;

    default:
        goto cleanup;
        break;
    }

	return count;
cleanup:
    return -EFAULT;
}


int init_recorded_processes_loader(void) {
    my_set_tsc_mode = (int (*)(unsigned int))  kallsyms_lookup_name("set_tsc_mode");
    IF_TRUE_CLEANUP(NULL == my_set_tsc_mode, "Failed to find set_tsc_mode!");

    recorded_processes_proc_ent = proc_create(PROC_NAME, 0666, NULL, &recorded_processes_proc_ops);
    IF_TRUE_CLEANUP(NULL == recorded_processes_proc_ent, "Failed to create proc entry!");

    return 0;
cleanup:
    return -1;
}


void remove_recorded_processes_loader(void) {
    remove_proc_entry(PROC_NAME, NULL);
}