#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/mutex.h>
#include <linux/wait.h>
#include <linux/slab.h>

#include "utils.h"
#include "syscall_recorder.h"
#include "copy_to_user_wrapper.h"
#include "syscall_dumper.h"

#define PROC_NAME "syscall_dumper"

struct proc_dir_entry * proc_ent = NULL;

/*
 * @purpose: return the length that the dump of the recieved syscall will be.
 */
unsigned long get_record_len(struct syscall_record *syscall_record);

/*
 * @purpose: Dump all copy records of a specific syscall record.
 */
int dump_copy_records(struct syscall_record *syscall_record, char __user *buf);

/*
 * @purpose: Dump the syscall record (without copy record)
 */
int dump_syscall_record(struct syscall_record *syscall_record, char __user *buf);


#define GENERAL_DUMP_ERROR 1
#define SHORT_WRITE_ERROR 2
/*
 * @purpose: Dump A SINGLE syscall record (syscall + copies)
 * 
 * @return:
 *      -GENERAL_DUMP_ERROR: Something bad happened
 *      -SHORT_WRITE_ERROR: Recieved buffer was too short for a record
 *      else:
 *          The size of the dump written to user.
 */
ssize_t dump_single_record(char __user *buf, size_t size);

/*
 * @purpose: Dump to user the maximum amount of syscall records that can 
 *              be written in size;
 * 
 * @return:
 *  -EINVAL: There wasn't enough space to write even a single record.
 *  -EFAULT: A general error accuured.
 *  <positive number>: The amount of bytes dumped in records.
 *  -
 */
ssize_t dump_records(char __user *buf, size_t size);

/*
 * @purpose: file operation to run when /proc/syscall_dumper is read.
 */
ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos);

struct file_operations proc_ops = {
	.read = read_proc,
};

unsigned long get_record_len(struct syscall_record *syscall_record) {
    
    unsigned long size = sizeof(struct syscall_dump);
    struct copy_record_element *copy_record_element;

    list_for_each_entry(copy_record_element, &(syscall_record->copies_to_user), list) {
        size += sizeof(struct copy_record) + copy_record_element->record.len;
    }
    
    return size;
}

int dump_copy_records(struct syscall_record *syscall_record, char __user *buf) {

    struct copy_record_element *copy_record_element;
    unsigned int record_size;

    list_for_each_entry(copy_record_element, &(syscall_record->copies_to_user), list) {
        record_size = sizeof(struct copy_record) + copy_record_element->record.len;
        IF_TRUE_CLEANUP(0 != copy_to_user(buf, &(copy_record_element->record), record_size),
                            "Failed to dump copy record!");

        buf += record_size;
    }

    return 0;

cleanup:
    return -1;
}

int dump_syscall_record(struct syscall_record *syscall_record, char __user *buf) {
    struct syscall_dump syscall_dump;
    int ret = -1;

    syscall_dump.ret = syscall_record->ret;
    syscall_dump.userspace_regs = syscall_record->userspace_regs;
    syscall_dump.copies_amount = syscall_record->amount_of_copies;

    IF_TRUE_CLEANUP(0 != copy_to_user(buf, &syscall_dump, sizeof(struct syscall_dump)),
                        "Failed to copy syscall record to user!");

    ret = 0;

cleanup:
    return ret;
}

ssize_t dump_single_record(char __user *buf, size_t size) {
    struct syscall_record *syscall_record;
    unsigned long len;

    IF_TRUE_CLEANUP(
        sizeof(syscall_record) !=
        kfifo_out(&recorded_syscalls, &(syscall_record), sizeof(syscall_record)),
        "Failed to read from fifo enough elements :(");

    len = get_record_len(syscall_record);
    IF_TRUE_GOTO(size < len, cleanup_short_write);
    
    IF_TRUE_CLEANUP(dump_syscall_record(syscall_record, buf), "Failed to dump syscall!");
    buf += sizeof(struct syscall_dump);

    IF_TRUE_CLEANUP(dump_copy_records(syscall_record, buf), "Failed to dump syscall copies!");

    free_syscall_record(syscall_record);
    return len;
cleanup_short_write:
    return -SHORT_WRITE_ERROR;
cleanup:
    free_syscall_record(syscall_record);
    return -GENERAL_DUMP_ERROR;
}

ssize_t dump_records(char __user *buf, size_t size) {
    ssize_t size_written = 0;
    ssize_t dump_ret;
    int did_do_first_write = 0;
    do {
        dump_ret = dump_single_record(buf, size);
        switch (dump_ret)
        {
            case -SHORT_WRITE_ERROR:
                /* If any record after the first was too long,
                   Its still success... */
                return did_do_first_write ? size_written : -EINVAL;
                break;

            case -GENERAL_DUMP_ERROR:
                return -EFAULT;
                break;
            
            default:
                buf += dump_ret;
                size -= dump_ret;
                size_written += dump_ret;
                did_do_first_write = 1;
        }
    } while (!kfifo_is_empty(&recorded_syscalls));
    return size_written;
}

ssize_t read_proc(struct file *file, char __user *buf, size_t size, loff_t *ppos) {
    DEFINE_WAIT(wait);
    ssize_t ret;
    
    add_wait_queue(&recorded_syscalls_wait, &wait);

    mutex_lock(&recorded_syscalls_mutex);
    while (kfifo_is_empty(&recorded_syscalls))
    {
        mutex_unlock(&recorded_syscalls_mutex);
        prepare_to_wait(&recorded_syscalls_wait, &wait, TASK_INTERRUPTIBLE);

        schedule();
        
        // TODO Make sure we did dis good
        // If woken up from signal
        IF_TRUE_GOTO(signal_pending(current), cleanup_signal);

        mutex_lock(&recorded_syscalls_mutex);       
    }

    finish_wait(&recorded_syscalls_wait, &wait);

    ret = dump_records(buf, size);
    mutex_unlock(&recorded_syscalls_mutex);

    return ret;

cleanup_signal:
    LOG("Cleanup signal");
    finish_wait(&recorded_syscalls_wait, &wait);
    return -ERESTARTSYS;
}

int init_syscall_dumper(void) {
    // TODO WTF IS THE RIGHT PERMISSIONS?
    proc_ent = proc_create(PROC_NAME, 0666, NULL, &proc_ops);
    IF_TRUE_CLEANUP(NULL == proc_ent, "Failed to create proc entry!");

    return 0;
cleanup:
    return -1;
}

void remove_syscall_dumper(void) {
    remove_proc_entry(PROC_NAME, NULL);
}