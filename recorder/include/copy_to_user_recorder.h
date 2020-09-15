#ifndef COPY_TO_USER_RECORDER_H
#define COPY_TO_USER_RECORDER_H

#include <linux/kernel.h>

struct copy_to_user_event {
    void * from;
    void * to;
    unsigned long len;
    unsigned char bytes[];
};

int init_copy_to_user_record(void);
void unload_copy_to_user_record(void);

int copy_to_user_start_recording_pid(pid_t pid);
void copy_to_user_stop_recording_pid(pid_t pid);

#endif