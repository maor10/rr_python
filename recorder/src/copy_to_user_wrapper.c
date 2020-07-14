#include <linux/kprobes.h>
#include <linux/list.h>

#include "utils.h"
#include "copy_to_user_wrapper.h"
#include "syscall_hooker.h"
#include "recorded_processes_loader.h"

int pre_put(struct kretprobe_instance * probe, struct pt_regs *regs);
int post_put(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Record all data kernel copies to userspace processes we record
 * 
 * @notes: 
 *      - Runs at the beggining of every copy_to_user called on system.
 *      - The pre_copy function should just record copy params and not save
 *          them yet, because only in post_copy we know if copy suceeded.
 * 
 * @ret: 
 *      1 == run post_copy after syscall is done
 *      0 == don't run post_copy after syscall
 */
int pre_copy(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Runs AFTER copy_to_user, and if it was successfull,
 *              record copied data for recording..
 */
int post_copy(struct kretprobe_instance *probe, struct pt_regs *regs);


struct kretprobe copy_kretprobe = {
        .kp.symbol_name	= "_copy_to_user",
        .entry_handler 	= pre_copy,
        .handler		= post_copy,
        .maxactive		= 1000
};

struct kretprobe copyout_kretprobe = {
        .kp.symbol_name	= "copyout",
        .entry_handler 	= pre_copy,
        .handler		= post_copy,
        .maxactive		= 1000
};

struct kretprobe * copy_kretprobes[] = {&copy_kretprobe, &copyout_kretprobe};

struct kretprobe put_user_1_kretprobes = {
        .kp.symbol_name	= "__put_user_1",
        .entry_handler 	= pre_put,
        .handler		= post_put,
        .maxactive		= 1000,
        .data_size      = 1
};

struct kretprobe put_user_2_kretprobes = {
        .kp.symbol_name	= "__put_user_2",
        .entry_handler 	= pre_put,
        .handler		= post_put,
        .maxactive		= 1000,
        .data_size      = 2
};

struct kretprobe put_user_4_kretprobes = {
        .kp.symbol_name	= "__put_user_4",
        .entry_handler 	= pre_put,
        .handler		= post_put,
        .maxactive		= 1000,
        .data_size      = 4
};

struct kretprobe put_user_8_kretprobes = {
        .kp.symbol_name	= "__put_user_8",
        .entry_handler 	= pre_put,
        .handler		= post_put,
        .maxactive		= 1000,
        .data_size      = 8
};

struct kretprobe * put_user_kretprobes[] = {
    &put_user_1_kretprobes, &put_user_2_kretprobes,
    &put_user_4_kretprobes, &put_user_8_kretprobes
};

struct copy_record_element * current_copy = NULL;

void free_copy_record(struct copy_record_element * copy_record) {
    kfree(copy_record);
}

union put_data {
    uint8_t byte;
    uint16_t word;
    uint32_t dword;
    uint64_t qword;
};

int pre_put(struct kretprobe_instance * probe, struct pt_regs *regs) {
    union put_data * new_data;
    unsigned long copy_len;

    IF_TRUE_CLEANUP(current->pid != recorded_process_pid || recorded_process_pid == 0);
    IF_TRUE_CLEANUP(NULL == current_syscall_record);
    IF_TRUE_CLEANUP(NULL != current_copy, "ERROR! Can only record one copy at the same time!");

    copy_len = probe->rp->data_size;
    
    current_copy = kmalloc(sizeof(struct copy_record_element) + copy_len, GFP_KERNEL);
    current_copy->record.from = (void *) NULL;
    current_copy->record.to = (void *) regs->cx;
    current_copy->record.len = copy_len;
    new_data = (union put_data *) current_copy->record.bytes;
    
    switch (copy_len) {
        case 1:
            new_data->byte = regs->ax;
            break;
        case 2:
            new_data->word = regs->ax;
            break;
        case 4:
            new_data->dword = regs->ax;
            break;
        case 8:
            new_data->qword = regs->ax;
            break;
    }

    return 0;

cleanup:
    return 1;
}

int post_put(struct kretprobe_instance *probe, struct pt_regs *regs) {
    IF_TRUE_CLEANUP(regs_return_value(regs), "copy_to_user failed! not saving.");

    list_add_tail(&current_copy->list, &(current_syscall_record->copies_to_user));
    current_syscall_record->amount_of_copies++;
    
    // If we put every thing in list like we want we don't want to free element
    goto cleanup_without_free;

cleanup:
    kfree(current_copy);

cleanup_without_free:
    current_copy = NULL;

	return 0;
}

int pre_copy(struct kretprobe_instance * probe, struct pt_regs *regs) {
    
    unsigned long copy_len = (unsigned long) regs->dx;

    IF_TRUE_CLEANUP(current->pid != recorded_process_pid || recorded_process_pid == 0);
    IF_TRUE_CLEANUP(NULL == current_syscall_record);
    IF_TRUE_CLEANUP(NULL != current_copy, "ERROR! Can only record one copy at the same time!");
    // IF_TRUE_CLEANUP(0 == copy_len, "ERROR! Trying to copy something with 0 len!");

    current_copy = kmalloc(sizeof(struct copy_record_element) + copy_len, GFP_KERNEL);
    IF_TRUE_CLEANUP(NULL == current_copy, "Failed to alloc current copy!");
    
    current_copy->record.from = (void *) regs->si;
    current_copy->record.to = (void *) regs->di;
    current_copy->record.len = copy_len;

	return 0;

cleanup:
    return 1;
}


int post_copy(struct kretprobe_instance *probe, struct pt_regs *regs) {

    IF_TRUE_CLEANUP(regs_return_value(regs), "copy_to_user failed! not saving.");

    if (current_copy->record.len > 0) {
        memcpy(current_copy->record.bytes, current_copy->record.from, current_copy->record.len);
    }

    list_add_tail(&current_copy->list, &(current_syscall_record->copies_to_user));
    current_syscall_record->amount_of_copies++;
    
    // If we put every thing in list like we want we don't want to free element
    goto cleanup_without_free;

cleanup:
    kfree(current_copy);

cleanup_without_free:
    current_copy = NULL;

	return 0;
}

int init_copy_hook(void) {
	IF_TRUE_CLEANUP(
        0 > register_kretprobes(copy_kretprobes, sizeof(copy_kretprobes) / sizeof(struct kretprobe *)),
        "Failed to init copy kprobe!"
    );

    IF_TRUE_CLEANUP(
        0 > register_kretprobes(put_user_kretprobes, sizeof(put_user_kretprobes) / sizeof(struct kretprobe *)),
        "Failed to init put kprobe!"
    );

    return 0;

cleanup:
    return -1;
}

void remove_copy_hook(void)
{
   	unregister_kretprobes(copy_kretprobes, sizeof(copy_kretprobes));
    unregister_kretprobes(put_user_kretprobes, sizeof(put_user_kretprobes));
}
