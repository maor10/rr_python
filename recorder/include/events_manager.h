#ifndef EVENTS_MANAGER
#define EVENTS_MANAGER

#include <linux/types.h>


#define EVENT_ID_RDTSC          (0)
#define EVENT_ID_SYSCALL_START  (1)
#define EVENT_ID_SYSCALL_DONE   (2)
#define EVENT_ID_COPY_TO_USER   (3)

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

/*
 * This data type points to the place in struct recorded_event where
 *      specific event data should be written to.
 */
typedef void event_data;

extern struct wait_queue_head recorded_events_wait;

/*
 * @purpose: The following function creates an event object.
 * 
 * @params:
 *      event_id:   One of the defined event ids.
 *      pid:        The pid of the process where event happened in.
 *      event_len:  The length of the event data (specific to every event_id).
 * 
 * @return: This function returns a pointer to where event data should be written to.
 */
event_data * create_event(uint8_t event_id, pid_t pid, unsigned int event_len);

/*
 * @purpose: Destroy an event.
 * 
 * @params:
 *      event:      Pointer to event_data (!!!!!) -- not struct recorded_event.
 */
void destroy_event(event_data *event);

/*
 * @purpose: Add an event to recorded events fifo.
 * 
 * @params:
 *      event:      Pointer to event data of event that should be added
 */
int add_event(event_data *event);

/*
 * @purpose: Is events fifo empty.
 */
int is_events_empty(void);

/*
 * @purpose: Dump as many events to userspace
 */
ssize_t dump_events(char * __user addr, int max_size);

/*
 * @purpose: Initialize the events engine
 */
int init_events(void);

/*
 * @purpose: Unload the events engine
 */
void unload_events(void);

#endif