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


int main(int argc, char *argv[]) {
  if (argc != 4) {
    printf("You must run this program with 4 variables\n");
    return -1;
  }
  int i;
  int length = atoi(argv[1]);
  int expected_return_value = atoi(argv[2]);
  char *expected_buffer = argv[3];
  int fd = -1;
  char *buffer = malloc(length);
  ssize_t size;

  kill(getpid(), SIGSTOP);

  size = read(fd, buffer, length);

  if (size != expected_return_value) {
    return -1;
  }

  if (strcmp(buffer, expected_buffer) != 0) {
    return -1;
  }

  return 0;
}