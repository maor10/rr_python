#include <signal.h>
#include <stdio.h>


int main() {
  char buffer[100];
  printf("%lu\n", (unsigned long)buffer);
  fflush(stdout);
  // first sigstop is for when ptrace connects and send cont, second is to stop so tester can do his stuff
  raise(SIGSTOP);
  raise(SIGSTOP);
  return 0;
}