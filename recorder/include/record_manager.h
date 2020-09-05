#ifndef RECORD_MANAGER
#define RECORD_MANAGER

int start_recording_pid(pid_t pid);
int stop_recording_pid(pid_t pid);

int is_pid_recorded(pid_t pid);

int init_recording(void);
void unload_recording(void);

#endif