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

  char buffer[5];

  ssize_t size;

  printf("test - Waiting....\n");
  raise(SIGSTOP);
  printf("test - Continuing!\n");

  size = read(fd, buffer, length);

  if (size != expected_return_value) {
    fprintf( stderr, "Expected %d, got %ld\n", expected_return_value, size);
    return -1;
  }

  if (strcmp(buffer, expected_buffer) != 0) {
    fprintf( stderr, "Expected %s, got %s\n", expected_buffer, buffer);
    return -1;
  }

  printf("FunFun\n");
  return 0;
}