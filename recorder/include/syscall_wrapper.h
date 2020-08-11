#ifndef SYSCALL_WRAPPER_H
#define SYSCALL_WRAPPER_H

/* The following macro let's you define a syscall wrapper..
 * @NOTE : After decalring the wrapper you still need to add it to 
 *          syscall_wrappers array :)
 */
#define DEFINE_WRAPPER(WRAPPER_NAME, SYSCALL_NAME, CALLBACK_FUNC)       \
struct syscall_wrapper WRAPPER_NAME = {                                 \
    .get_record_mem_callback    = CALLBACK_FUNC,                        \
    .retprobe.kp.symbol_name	= SYSCALL_NAME,                         \
    .retprobe.entry_handler 	= pre_wrap_syscall,                     \
    .retprobe.handler		    = post_wrap_syscall,                    \
    .retprobe.maxactive	    	= 1000,                                 \
    .retprobe.data_size	    	= sizeof(struct poll_recorded_mem *),   \
}

/*
 * @purpose: Init all the system calls wrappers 
 */
int init_syscall_wrappers(void);

/*
 * @purpose: Remove all system calls wrappers
 */
void remove_syscall_wrappers(void);

#endif