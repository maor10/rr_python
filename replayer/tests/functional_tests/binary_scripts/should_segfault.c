#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>


int main() {
  char buffer[100];
  printf("%lu\n", (unsigned long)buffer);
  fflush(stdout);
  kill(getpid(), SIGSTOP);
  printf("HELLO!\n");
  memcpy((void*)-1, buffer, 10000);
  return 0;
}
