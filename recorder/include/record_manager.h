#ifndef RECORD_MANAGER
#define RECORD_MANAGER

extern int recorded_process_pid;

/*
 * @purpose: Ask record engine to start recording a pid
 */
int start_recording_pid(pid_t pid);

/*
 * @purpose: Ask record engine to stop recording a pid
 */
int stop_recording_pid(pid_t pid);

int is_pid_recorded(pid_t pid);

int init_recording(void);
void unload_recording(void);

#endif