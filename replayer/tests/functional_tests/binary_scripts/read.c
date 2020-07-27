#include <signal.h>
#include <stdio.h>
#include <unistd.h>


int main() {
  char buffer[100];
  printf("%lu\n", (unsigned long)buffer);
  fflush(stdout);
  kill(getpid(), SIGSTOP);
  read(0, buffer, 100);
  return 0;
}
