#include <stdio.h>
#include <openssl/rand.h>
#include <signal.h>


int main() {
	char bytes[10] = {0};
	int i;
	printf("stopped \n");
	kill(getpid(), SIGSTOP);
	printf("continued \n");
	i = RAND_bytes(bytes, 10);
	if (i == 0) {
		printf("oh :/\n");
	}

	printf("%i\n", i);
	printf("%x %x %x\n", bytes[0], bytes[1], bytes[2]);
}
