#include <stdio.h>
#include <openssl/rand.h>

int main() {
	char bytes[10] = {0};
	int i = RAND_bytes(bytes, 10);
	if (i == 0) {
		printf("oh :/\n");
	}
	printf("%i\n", i);
	printf("%c %c %c\n", bytes[0], bytes[1], bytes[2]);
}
