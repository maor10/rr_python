#ifndef RECORDING_CONTROL_PROCFILE
#define RECORDING_CONTROL_PROCFILE

/*
 * @purpose: Create the proc file to load recorded processes
 */
int init_recording_control_procfile(void);

/*
 * @purpose: Destroy the proc file to load recorded processes
 */
void unload_recording_control_procfile(void);

#endif