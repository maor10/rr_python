#ifndef SYSCALL_WRAPPER_H
#define SYSCALL_WRAPPER_H

/*
 * @purpose: Init all the system calls wrappers 
 */
int init_syscall_wrappers(void);

/*
 * @purpose: Remove all system calls wrappers
 */
void remove_syscall_wrappers(void);

#endif