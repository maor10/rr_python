#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <ctype.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/ptrace.h>
#include <poll.h>



int main(int argc, char *argv[]) {
  if (argc != 2) {
    printf("You must run this program with 4 variables\n");
    return -1;
  }
  int expected_poll_result = atoi(argv[1]);
  struct pollfd poll_fd = {
    .fd = 3,
    .events = POLLIN,
    .revents = 100
  };
  struct msghdr *message
  int res;

  kill(getpid(), SIGSTOP);

  res = poll(&poll_fd, 1, 1);
  // res = syscall(7, &poll_fd, 1, 1);


  if (res == -1) {
    _exit(1);
    return -1;
  }

  if (expected_poll_result != poll_fd.revents) {
    _exit(1);
    return -1;
  }

  _exit(0);
  return 0;
}