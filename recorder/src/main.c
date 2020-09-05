#include <linux/module.h>
#include <linux/kernel.h>

#include "utils.h"
#include "record_manager.h"
#include "events_manager.h"

MODULE_LICENSE("GPL");

static int __init recorder_init(void) {

	LOG("Initializing recorder...");

	IF_TRUE_CLEANUP(init_events(), "Failed to init events manager!");
	IF_TRUE_GOTO(init_recording(), cleanup_events, "Failed to init recording!");
	
	return 0;

cleanup_events:
	unload_events();

cleanup:
	return -1;
}

static void __exit recorder_exit(void) {
	// TODO WHAT HAPPENS IF WE REMOVE WHILE IN HOOK?
	unload_recording();
	unload_events();
	
	return;
}

module_init(recorder_init);
module_exit(recorder_exit);
