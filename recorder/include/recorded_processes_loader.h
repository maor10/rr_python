#ifndef RECORDED_PROCESSES_LOADER_H
#define RECORDED_PROCESSES_LOADER_H


extern int recorded_process_pid;


/*
 * @purpose: Create the proc file to load recorded processes
 */
int init_recorded_processes_loader(void);

/*
 * @purpose: Destroy the proc file to load recorded processes
 */
void remove_recorded_processes_loader(void);

#endif