#ifndef WRAPPED_COPY_TO_USER_RECORDER
#define WRAPPED_COPY_TO_USER_RECORDER

#include <linux/kprobes.h>


// See docs for explenation
struct copy_wrapper {
    int (*get_record_mem_callback) (struct pt_regs *, void * __user *, unsigned long *);
    struct kretprobe retprobe;
};

/* The following macro let's you define a wrapped copy_to_user func..
 * @NOTE : After decalring the wrapper you still need to add it to 
 *          wrappers array :)
 */
#define DEFINE_WRAPPER(WRAPPER_NAME, FUNC_TO_HOOK, CALLBACK_FUNC)       \
struct copy_wrapper WRAPPER_NAME = {                                 \
    .get_record_mem_callback    = CALLBACK_FUNC,                        \
    .retprobe.kp.symbol_name	= FUNC_TO_HOOK,                         \
    .retprobe.entry_handler 	= pre_copy_wrapper,                     \
    .retprobe.handler		    = post_copy_wrapper,                    \
    .retprobe.maxactive	    	= 1,                                 \
    .retprobe.data_size	    	= sizeof(struct poll_recorded_mem *),   \
}


int init_wrapped_copy_to_user_record(void);
void unload_wrapped_copy_to_user_record(void);
int wrapped_copy_to_user_start_recording_pid(pid_t pid);
void wrapped_copy_to_user_stop_recording_pid(pid_t pid);


#endif