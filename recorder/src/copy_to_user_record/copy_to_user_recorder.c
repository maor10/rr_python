#include <linux/kprobes.h>

#include "copy_to_user_recorder.h"
#include "record_manager.h"
#include "events_manager.h"
#include "utils.h"


/*
 * @purpose: Record all data kernel puts to userspace in processes we record
 * 
 * @notes: 
 *      - Runs at the beggining of every put_user called on system.
 *      - The pre_put function should just record put params, and wait for 
 *          post_put to see if to put in syscalls writes.
 * 
 * @ret: 
 *      1 == run post_put after syscall is done
 *      0 == don't run post_put after syscall
 */
int pre_put(struct kretprobe_instance * probe, struct pt_regs *regs);

/*
 * @purpose: Record all data kernel puts to userspace in processes we record
 * 
 * @notes: 
 *      - Runs at the after of every put_user we hooked and returned 0.
 *      - The function takes saved put user and saves it to list
 */
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
        // We need to save event to only add it if copy was success
        .data_size      = sizeof(struct recorded_event *),
        .maxactive		= 1000
};

struct kretprobe copyout_kretprobe = {
        .kp.symbol_name	= "copyout",
        .entry_handler 	= pre_copy,
        .handler		= post_copy,
        // We need to save event to only add it if copy was success
        .data_size      = sizeof(struct recorded_event *),
        .maxactive		= 1000
};

struct kretprobe put_user_1_kretprobes = {
        .kp.symbol_name	= "__put_user_1",
        .entry_handler 	= pre_put,
        .handler		= post_copy,
        .maxactive		= 1000,
        // Document the fuck why we use + 1
        .data_size      = sizeof(struct recorded_event *) + 1,
};

struct kretprobe put_user_2_kretprobes = {
        .kp.symbol_name	= "__put_user_2",
        .entry_handler 	= pre_put,
        .handler		= post_copy,
        .maxactive		= 1000,
        .data_size      = sizeof(struct recorded_event *) + 2,
};

struct kretprobe put_user_4_kretprobes = {
        .kp.symbol_name	= "__put_user_4",
        .entry_handler 	= pre_put,
        .handler		= post_copy,
        .maxactive		= 1000,
        .data_size      = sizeof(struct recorded_event *) + 4,
};

struct kretprobe put_user_8_kretprobes = {
        .kp.symbol_name	= "__put_user_8",
        .entry_handler 	= pre_put,
        .handler		= post_copy,
        .maxactive		= 1000,
        .data_size      = sizeof(struct recorded_event *) + 8,
};

struct kretprobe * copy_kretprobes[] = {
    &copy_kretprobe, &copyout_kretprobe,
    &put_user_1_kretprobes, &put_user_2_kretprobes,
    &put_user_4_kretprobes, &put_user_8_kretprobes
};


union put_data {
    uint8_t byte;
    uint16_t word;
    uint32_t dword;
    uint64_t qword;
};

int pre_put(struct kretprobe_instance * probe, struct pt_regs *regs) {
    struct copy_to_user_event *new_event = NULL;
    union put_data * put_data;
    unsigned long copy_len;

    IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));
    
    copy_len = probe->rp->data_size - sizeof(struct recorded_event *);

    new_event = (struct copy_to_user_event *)create_event(EVENT_ID_COPY_TO_USER, current->pid, sizeof(struct copy_to_user_event) + copy_len);
    IF_TRUE_CLEANUP(NULL == new_event, "Failed to allocate new event!");

    new_event->from = (void *) NULL;
    new_event->to = (void *) regs->cx;
    new_event->len = copy_len;

    put_data = (union put_data *) new_event->bytes;
    switch (copy_len) {
        case 1:
            put_data->byte = regs->ax;
            break;
        case 2:
            put_data->word = regs->ax;
            break;
        case 4:
            put_data->dword = regs->ax;
            break;
        case 8:
            put_data->qword = regs->ax;
            break;
    }

    memcpy(probe->data, &new_event, sizeof(new_event));

    return 0;

cleanup:
    if (NULL != new_event) {
        destroy_event(new_event);
    }

    return 1;
}

int pre_copy(struct kretprobe_instance * probe, struct pt_regs *regs) {
    struct copy_to_user_event *new_event;
    
    unsigned long copy_len = (unsigned long) regs->dx;

    IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));

    new_event = (struct copy_to_user_event *)create_event(EVENT_ID_COPY_TO_USER, current->pid, sizeof(struct copy_to_user_event) + copy_len);
    IF_TRUE_CLEANUP(NULL == new_event, "Failed to allocate new event!");
    
    new_event->from = (void *) regs->si;
    new_event->to = (void *) regs->di;
    new_event->len = copy_len;

    memcpy(new_event->bytes, new_event->from, new_event->len);

    memcpy(probe->data, &new_event, sizeof(new_event));
    return 0;

cleanup:
    return 1;
}


int post_copy(struct kretprobe_instance *probe, struct pt_regs *regs) {
    struct copy_to_user_event *new_event;

    memcpy(&new_event, probe->data, sizeof(new_event));

    IF_TRUE_CLEANUP(regs_return_value(regs), "copy failed! not saving.");
    IF_TRUE_CLEANUP(add_event(new_event), "Failed to add new copy event!");

    return 0;

cleanup:
    if (NULL != new_event) {
        destroy_event(new_event);
    }

	return 0;
}

int init_copy_to_user_record(void) {
	IF_TRUE_CLEANUP(
        0 > register_kretprobes(copy_kretprobes, sizeof(copy_kretprobes) / sizeof(struct kretprobe *)),
        "Failed to init copy kprobe!"
    );
    
    return 0;

cleanup:
    return -1;
}

void unload_copy_to_user_record(void) {
    unregister_kretprobes(copy_kretprobes, sizeof(copy_kretprobes) / sizeof(struct kretprobe *));
}

int copy_to_user_start_recording_pid(pid_t pid) {
    return 0;
}

void copy_to_user_stop_recording_pid(pid_t pid) {
    return;
}
