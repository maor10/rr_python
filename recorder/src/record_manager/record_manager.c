#include <linux/types.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/kfifo.h>

#include "record_manager.h"
#include "recording_control_procfile.h"
#include "rdtsc_recorder.h"
#include "syscall_recorder.h"
#include "copy_to_user_recorder.h"
#include "wrapped_copy_to_user_recorder.h"
#include "utils.h"


struct recorder {
    char * name;
    int (*init)(void);
    void (*unload)(void);
    int (*start_recording_pid)(pid_t pid);
    void (*stop_recording_pid)(pid_t pid);
};

struct recorder recorders[] = {
    {
        .name                   = "rdtsc recorder",
        .init                   = init_rdtsc_record,
        .unload                 = unload_rdtsc_record,
        .start_recording_pid    = rdtsc_start_recoding_pid,
        .stop_recording_pid     = rdtsc_stop_recording_pid
    },
    {
        .name                   = "syscalls recorder",
        .init                   = init_syscalls_record,
        .unload                 = unload_syscalls_record,
        .start_recording_pid    = syscalls_start_recording_pid,
        .stop_recording_pid     = syscalls_stop_recording_pid
    },
    {
        .name                   = "copy to user recorder",
        .init                   = init_copy_to_user_record,
        .unload                 = unload_copy_to_user_record,
        .start_recording_pid    = copy_to_user_start_recording_pid,
        .stop_recording_pid     = copy_to_user_stop_recording_pid
    },
    {
        .name                   = "wrapped_copy to user recorder",
        .init                   = init_wrapped_copy_to_user_record,
        .unload                 = unload_wrapped_copy_to_user_record,
        .start_recording_pid    = wrapped_copy_to_user_start_recording_pid,
        .stop_recording_pid     = wrapped_copy_to_user_stop_recording_pid
    }

};

unsigned int recorders_size = sizeof(recorders) / sizeof(struct recorder);

pid_t recorded_process_pid = -1;

int start_recording_pid(pid_t pid) {
    int i = 0;
    int current_recorder_idx = 0;

    // TODO IS THERE A RACE HERE???
    while (current_recorder_idx < recorders_size) {
        IF_TRUE_CLEANUP(recorders[i].start_recording_pid(pid),
            "Failed to start recording with recorder %s", recorders[i].name);
        current_recorder_idx++;
    }

    recorded_process_pid = pid;
    return 0;

cleanup:
    for (i = 0; i < current_recorder_idx; i++) {
        recorders[i].stop_recording_pid(pid);
    }
    return -1;
}

int stop_recording_pid(pid_t pid) {
    int i = 0;
    recorded_process_pid = -1;
    
    for (i=0; i < recorders_size; i++) {
        recorders[i].stop_recording_pid(pid);
    }

    return 0;
}

int is_pid_recorded(pid_t pid) {
    return recorded_process_pid == pid;
}

int init_recording(void) {
    int inited_recorder_idx = 0;
    int i = 0;
    
    while (inited_recorder_idx < recorders_size) {
        IF_TRUE_CLEANUP(recorders[inited_recorder_idx].init(),
                            "Failed to init recorder %s!", recorders[inited_recorder_idx].name);
        inited_recorder_idx++;
    }

    IF_TRUE_CLEANUP(init_recording_control_procfile(), "Failed to init procfile");

    return 0;

cleanup:
    for (i = 0; i < inited_recorder_idx; i++) {
        recorders[i].unload();
    }

    return -1;
}

void unload_recording(void) {
    int i;

    unload_recording_control_procfile();

    for (i = 0; i < recorders_size; i++) {
        recorders[i].unload();
    }
}