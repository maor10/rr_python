#define _GNU_SOURCE
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>
#include <crypto/rand.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <dlfcn.h>
#include <string.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <stdbool.h>
#include <stdlib.h>
#include <errno.h>
// struct rand_pool_st {
//     unsigned char *buffer;  /* points to the beginning of the random pool */
//     size_t len; /* current number of random bytes contained in the pool */

//     int attached;  /* true pool was attached to existing buffer */
//     int secure;    /* 1: allocated on the secure heap, 0: otherwise */

//     size_t min_len; /* minimum number of random bytes requested */
//     size_t max_len; /* maximum number of random bytes (allocated buffer size) */
//     size_t alloc_len; /* current number of bytes allocated */
//     size_t entropy; /* current entropy count in bits */
//     size_t entropy_requested; /* requested entropy count in bits */
// };
// typedef struct rand_pool_st RAND_POOL;
// // Compile and link with -pthread.
static int (*real_rand_pool_add)(RAND_POOL *pool,
                  const unsigned char *buffer, size_t len, size_t entropy) = NULL;

int rand_pool_add_additional_data(RAND_POOL *pool) {

  struct {
        int fork_id;
        CRYPTO_THREAD_ID tid;
        uint64_t time;
    } data = { 0 };

    printf("OMGGGG GOT HEREEE\n");
    /*
     * Add some noise from the thread id and a high resolution timer.
     * The fork_id adds some extra fork-safety.
     * The thread id adds a little randomness if the drbg is accessed
     * concurrently (which is the case for the <master> drbg).
     */
    data.fork_id = getpid();
    data.tid = pthread_self();
    data.time = time(NULL);
    // return RAND_bytes(bytes, 10);    
    real_rand_pool_add = dlsym(RTLD_NEXT, "rand_pool_add");
    return real_rand_pool_add(pool, (unsigned char *)&data, sizeof(data), 0);
}

typedef ssize_t (*real_read_t)(int, void *, size_t);
ssize_t real_read(int fd, void *data, size_t size) {
  printf("I LIKE TO READ WHAT's ON TV\n");
  return ((real_read_t)dlsym(RTLD_NEXT, "read"))(fd, data, size);
}


int main() {
  printf("oh no?\n");
  return 0;
}