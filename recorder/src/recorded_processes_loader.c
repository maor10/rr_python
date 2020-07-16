#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/slab.h>

#include "utils.h"
#include "recorded_processes_loader.h"

#include <linux/moduleparam.h>
#include <linux/init.h>
#include <linux/uaccess.h>

#define PROC_NAME "recorded_process"
#define BUFFER_SIZE 100


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
    int size_written;
	char buf[BUFFER_SIZE];
	
    IF_TRUE_CLEANUP(*ppos > 0 || count > BUFFER_SIZE);
	IF_TRUE_CLEANUP(copy_from_user(buf, ubuf, count));
    IF_TRUE_CLEANUP(sscanf(buf, "%d", &recorded_process_pid) != 1);

    LOG("Beginning to scan for pid %d", recorded_process_pid);

	size_written = strlen(buf);
	*ppos = size_written;
	return size_written;
cleanup:
    return -EFAULT;
}


int init_recorded_processes_loader(void) {
    recorded_processes_proc_ent = proc_create(PROC_NAME, 0666, NULL, &recorded_processes_proc_ops);
    IF_TRUE_CLEANUP(NULL == recorded_processes_proc_ent, "Failed to create proc entry!");

    return 0;
cleanup:
    return -1;
}


void remove_recorded_processes_loader(void) {
    remove_proc_entry(PROC_NAME, NULL);
}