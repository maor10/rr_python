#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
#include <linux/ftrace.h>


#include "utils.h"
#include "rdtsc_recorder.h"
#include "recorded_processes_loader.h"

/*
 * @purpose: The following function is a switch to decide whether to run
 * 				the original do_general_protection or to run my_do_general_protection.
 */
void do_general_protection_switch(unsigned long ip, unsigned long parent_ip,
                   struct ftrace_ops *op, struct pt_regs *regs);

void my_do_general_protection(struct pt_regs *regs, long error_code);

#define FUNC_TO_HOOK "do_general_protection"
struct ftrace_ops do_general_protection_hook = {
      .func                    = do_general_protection_switch,
      .flags                   = FTRACE_OPS_FL_SAVE_REGS | FTRACE_OPS_FL_IPMODIFY
};


void my_do_general_protection(struct pt_regs *regs, long error_code) {	
	asm volatile("rdtsc" : "=a" (regs->ax), "=d" (regs->dx));

	// Skip rdtsc
	regs->ip += 2;

	return;
}

#define RDTSC_OPCODE 0x310F
void do_general_protection_switch(unsigned long ip, unsigned long parent_ip,
                   struct ftrace_ops *op, struct pt_regs *regs) {
	struct pt_regs *userspace_regs;
	short opcode;

	IF_TRUE_CLEANUP(current->pid != recorded_process_pid || recorded_process_pid == 0);

	userspace_regs = (struct pt_regs *) regs->di;
	IF_TRUE_CLEANUP(!user_mode(userspace_regs));
	
	IF_TRUE_CLEANUP(get_user(opcode, (short *)userspace_regs->ip), "Failed to get user opcode!");
	IF_TRUE_CLEANUP(RDTSC_OPCODE != opcode, "Not opcode :(\n");

	// Don't run original func -- run us :)
	regs->ip = (unsigned long) my_do_general_protection;

cleanup:
	return;
}

int init_rdtsc_record(void) {
    IF_TRUE_CLEANUP(
		ftrace_set_filter(&do_general_protection_hook, FUNC_TO_HOOK, strlen(FUNC_TO_HOOK), 0),
		"Failed to set filter to ftrace!");
	
	IF_TRUE_CLEANUP(register_ftrace_function(&do_general_protection_hook), "Failed to register ftrace");

	return 0;
cleanup:
	return -1;
}

void remove_rdtsc_record(void) {
	unregister_ftrace_function(&do_general_protection_hook);
}