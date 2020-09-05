#ifndef EVENTS_MANAGER
#define EVENTS_MANAGER

#include <linux/types.h>


#define EVENT_ID_RDTSC          (0)
#define EVENT_ID_SYSCALL_START  (1)
#define EVENT_ID_SYSCALL_DONE   (2)

/*
 * Contains the recorded nondeterministic event relevant data to be dumped.
 */
struct __packed recorded_event_dump {
    long pid;
    uint8_t event_id;
    uint8_t event[];
};

/*
 * A record of a single nondeterministic event.
 */
struct recorded_event {
    unsigned int len;
    struct recorded_event_dump event_dump;
};

struct recorded_event * create_event(uint8_t event_id, pid_t pid, unsigned int event_len);
void destroy_event(struct recorded_event *event);

struct recorded_event * read_event(int blocking);
int add_event(struct recorded_event *event);

int init_events(void);
void unload_events(void);

#endif