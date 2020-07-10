#ifndef RECORDED_PROCESSES_LOADER_H
#define RECORDED_PROCESSES_LOADER_H


extern int recorded_process_pid;


/*
 * @purpose: Create the proc file to dump records.
 */
int init_recorded_processes_loader(void);

/*
 * @purpose: Destroy the proc file to dump records
 */
void remove_recorded_processes_loader(void);

#endif