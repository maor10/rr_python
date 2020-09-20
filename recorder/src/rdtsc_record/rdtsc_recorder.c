#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/ftrace.h>
#include <linux/kallsyms.h>
#include <linux/prctl.h>

#include "utils.h"
#include "record_manager.h"
#include "events_manager.h"
#include "rdtsc_recorder.h"

/*
 * @purpose: The following function is a switch to decide whether to run
 * 				the original do_general_protection or to run my_do_general_protection.
 */
void do_general_protection_switch(unsigned long ip, unsigned long parent_ip,
                   struct ftrace_ops *op, struct pt_regs *regs);

/* 
 * @purpose: Hook of do_general_protection when RDTSC is called
 * 				This function will emulate userpace RDTSC and record it
 * 
 */
void my_do_general_protection(struct pt_regs *regs, long error_code);

/*
 * @purpose: Record a rdtsc event.
 */
void record_rdtsc(unsigned long ax, unsigned long dx);

#define FUNC_TO_HOOK "do_general_protection"
struct ftrace_ops do_general_protection_hook = {
      .func                    = do_general_protection_switch,
      .flags                   = FTRACE_OPS_FL_SAVE_REGS | FTRACE_OPS_FL_IPMODIFY
};

/* 
 * Since function is not exported in kernel, we need to find it out selfs.
 */
int (*my_set_tsc_mode)(unsigned int val);

void record_rdtsc(unsigned long ax, unsigned long dx) {
	struct rdtsc_event *new_event;

	new_event = create_event(EVENT_ID_RDTSC, current->pid, sizeof(struct rdtsc_event));
	IF_TRUE_CLEANUP(NULL == new_event, "Failed to create rdtsc event");

	new_event->ax = ax;
	new_event->dx = dx;

	IF_TRUE_CLEANUP(add_event(new_event), "Failed to add rdtsc event!");

	return;

cleanup:
	if (NULL != new_event) {
		destroy_event(new_event);
	}
	return;
	
}

void my_do_general_protection(struct pt_regs *userspace_regs, long error_code) {	
	asm volatile("rdtsc" : "=a" (userspace_regs->ax), "=d" (userspace_regs->dx));

	record_rdtsc(userspace_regs->ax, userspace_regs->dx);

	// Skip usersapce rdtsc opcode after we emulated it
	userspace_regs->ip += 2;

	return;
}

#define RDTSC_OPCODE 0x310F
void do_general_protection_switch(unsigned long ip, unsigned long parent_ip,
                   struct ftrace_ops *op, struct pt_regs *regs) {
	struct pt_regs *userspace_regs;
	short opcode;

	IF_TRUE_CLEANUP(!is_pid_recorded(current->pid));

	userspace_regs = (struct pt_regs *) regs->di;
	IF_TRUE_CLEANUP(!user_mode(userspace_regs));
	
	IF_TRUE_CLEANUP(get_user(opcode, (short *)userspace_regs->ip), "Failed to get user opcode!");
	IF_TRUE_CLEANUP(RDTSC_OPCODE != opcode, "Not rdtsc opcode :(\n");

	// Don't run original func -- run us :)
	regs->ip = (unsigned long) my_do_general_protection;

cleanup:
	return;
}

// TODO SHOULD WE BACK UP VAlUE OF TSC MODE BEFORE????
int rdtsc_start_recoding_pid(pid_t pid) {
	return my_set_tsc_mode(PR_TSC_SIGSEGV);
}

void rdtsc_stop_recording_pid(pid_t pid) {
	my_set_tsc_mode(PR_TSC_ENABLE);
}

int init_rdtsc_record(void) {
	my_set_tsc_mode = (int (*)(unsigned int))  kallsyms_lookup_name("set_tsc_mode");
    IF_TRUE_CLEANUP(NULL == my_set_tsc_mode, "Failed to find set_tsc_mode!");

    IF_TRUE_CLEANUP(
		ftrace_set_filter(&do_general_protection_hook, FUNC_TO_HOOK, strlen(FUNC_TO_HOOK), 0),
		"Failed to set filter to ftrace!");
	
	IF_TRUE_CLEANUP(register_ftrace_function(&do_general_protection_hook), "Failed to register ftrace");

	return 0;
cleanup:
	return -1;
}

void unload_rdtsc_record(void) {
	unregister_ftrace_function(&do_general_protection_hook);
}