#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/kfifo.h>

#include "events_dump_procfile.h"
#include "utils.h"
#include "events_manager.h"


#define EVENTS_FIFO_SIZE (1 << 10)

DEFINE_MUTEX(recorded_events_mutex);
struct kfifo recorded_events;


struct recorded_event * create_event(unsigned char event_id, pid_t pid, unsigned int event_len) {
    struct recorded_event *new_event;
    
    new_event = kmalloc(sizeof(struct recorded_event) + event_len, GFP_ATOMIC);
	IF_TRUE_CLEANUP(NULL == new_event, "Failed to malloc new event!");
    new_event->len = event_len + sizeof(struct recorded_event_dump);
    new_event->event_dump.pid = pid;
	new_event->event_dump.event_id = event_id;

    return new_event;

cleanup:
    return NULL;

}

int add_event(struct recorded_event *event) {
    int ret = -1;

    mutex_lock(&recorded_events_mutex);
    IF_TRUE_CLEANUP(sizeof(struct recorded_event *) != 
            kfifo_in(&recorded_events, &event, sizeof(struct recorded_event *)),
            "Failed to insert event to kfifo!");
    ret = 0;

cleanup:
    mutex_unlock(&recorded_events_mutex);
    return ret;
}

struct recorded_event * read_event(int blocking) {
    struct recorded_event *ret;

    IF_TRUE_CLEANUP(kfifo_is_empty(&recorded_events));

    IF_TRUE_CLEANUP(sizeof(ret) != kfifo_out(&recorded_events, &(ret), sizeof(ret)), 
                            "Failed to read from kfifo");

    return ret;
cleanup:
    return NULL;
}

int init_events(void) {
    IF_TRUE_CLEANUP(kfifo_alloc(&recorded_events, EVENTS_FIFO_SIZE, GFP_KERNEL), "Failed to alloc kfifo!");
    IF_TRUE_GOTO(init_events_dump_procfile(), cleanup_events_kfifo, "Failed to init events dump procfile!");

    return 0;
    
cleanup_events_kfifo:
    kfifo_free(&recorded_events);
cleanup:
    return -1;
}

void unload_events(void) {
    unload_events_dump_procfile();
    kfifo_free(&recorded_events);
}
