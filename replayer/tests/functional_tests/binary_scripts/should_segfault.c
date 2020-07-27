#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>


int main() {
  char buffer[100];
  printf("%lu\n", (unsigned long)buffer);
  fflush(stdout);
  kill(getpid(), SIGSTOP);
  memcpy((void*)-1, buffer, 10000);
  return 0;
}
