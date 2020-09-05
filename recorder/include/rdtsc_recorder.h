#ifndef RDTSC_RECORDER_H
#define RDTSC_RECORDER_H

struct __packed rdtsc_event {
    unsigned long ax;
    unsigned long dx;
};

int rdtsc_start_recoding_pid(pid_t pid);
void rdtsc_stop_recording_pid(pid_t pid);

int init_rdtsc_record(void);
void unload_rdtsc_record(void);

#endif