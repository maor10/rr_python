#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/kfifo.h>
#include <linux/wait.h>


#include "events_dump_procfile.h"
#include "utils.h"
#include "events_manager.h"


#define EVENTS_FIFO_SIZE (1 << 10)

DEFINE_MUTEX(recorded_events_mutex);
struct kfifo recorded_events;
DECLARE_WAIT_QUEUE_HEAD(recorded_events_wait);


#define GENERAL_DUMP_ERROR 1
#define SHORT_WRITE_ERROR 2
ssize_t dump_single_event(char * __user addr, int max_size);


void * create_event(unsigned char event_id, pid_t pid, unsigned int event_len) {
    struct recorded_event *new_event;
    
    new_event = kmalloc(sizeof(struct recorded_event) + event_len, GFP_ATOMIC);
	IF_TRUE_CLEANUP(NULL == new_event, "Failed to malloc new event!");
    new_event->len = event_len + sizeof(struct recorded_event_dump);
    new_event->event_dump.pid = pid;
	new_event->event_dump.event_id = event_id;

    return new_event->event_dump.event;

cleanup:
    return NULL;

}

void destroy_event(void *event_data) {
    struct recorded_event_dump * recorded_event_dump =
            container_of(event_data, struct recorded_event_dump, event);

    
    struct recorded_event *event =
            container_of(recorded_event_dump, struct recorded_event, event_dump);

    kfree(event);
}

int add_event(void *event_data) {
    struct recorded_event_dump * recorded_event_dump =
            container_of(event_data, struct recorded_event_dump, event);

    
    struct recorded_event *event =
            container_of(recorded_event_dump, struct recorded_event, event_dump);

    int ret = -1;

    mutex_lock(&recorded_events_mutex);
    IF_TRUE_CLEANUP(sizeof(struct recorded_event *) != 
            kfifo_in(&recorded_events, &event, sizeof(struct recorded_event *)),
            "Failed to insert event to kfifo!");
    
    wake_up(&recorded_events_wait);

    ret = 0;

cleanup:
    mutex_unlock(&recorded_events_mutex);
    return ret;
}

int is_events_empty(void) {
    int ret;

    mutex_lock(&recorded_events_mutex);
    ret = kfifo_is_empty(&recorded_events);
    mutex_unlock(&recorded_events_mutex);

    return ret;
}

ssize_t dump_single_event(char * __user addr, int max_size) {
    ssize_t ret = -GENERAL_DUMP_ERROR;
    struct recorded_event *peek_event = NULL;
    struct recorded_event *event = NULL;

    mutex_lock(&recorded_events_mutex);

    IF_TRUE_GOTO(kfifo_is_empty(&recorded_events), cleanup_kfifo_empty);

    // First peek at kfifo to see if read is not too short.
    IF_TRUE_CLEANUP(sizeof(event) != kfifo_out_peek(&recorded_events, &(peek_event), sizeof(peek_event)), 
                            "Failed to read from kfifo");

    IF_TRUE_GOTO(peek_event->len > max_size, cleanup_short_write);

    IF_TRUE_CLEANUP(sizeof(event) != kfifo_out(&recorded_events, &(event), sizeof(event)), 
                            "Failed to read from kfifo");

    IF_TRUE_CLEANUP(0 != copy_to_user(addr, &(event->event_dump), event->len),
                        "Failed to copy to user!");
    
    ret = event->len;
    goto cleanup;

cleanup_kfifo_empty:
    ret = 0;
    goto cleanup;

cleanup_short_write:
    ret = -SHORT_WRITE_ERROR;
    goto cleanup;

cleanup:
    if (NULL != event) {
        kfree(event);
    }

    mutex_unlock(&recorded_events_mutex);
    return ret;

}

ssize_t dump_events(char * __user addr, int max_size) {
    ssize_t ret = 0;
    ssize_t current_dump_ret;
    int did_do_first_write = 0;

    while (1) {
        current_dump_ret = dump_single_event(addr, max_size);
        
        switch (current_dump_ret) {
            case -SHORT_WRITE_ERROR:
                return did_do_first_write ? ret : -EINVAL;

            case -GENERAL_DUMP_ERROR:
                return -EFAULT;
            
            case 0:
                return ret;
        }

        did_do_first_write = 1;
        addr += current_dump_ret;
        ret += current_dump_ret;
    }
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
