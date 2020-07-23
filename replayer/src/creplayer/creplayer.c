#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/ptrace.h>
#include <linux/ptrace.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>

#include "utils.h"
#include <sys/signal.h>
#include <poll.h>


/**
 * Python module
 **/
PyObject *module = NULL;



/**
 * @purpose: Attach to the tracee and begin program execution
 * 
 **/
PyObject* attach_to_tracee_and_begin(pid_t pid) {
  LOG("Attaching...");
  
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_ATTACH, pid, 0, 0) == -1);
  waitpid(pid, 0, 0);
  
  LOG("Send PTRACE_CONT...");

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_CONT, pid, 0, 0) == -1);
  waitpid(pid, 0, 0);
  
  Py_RETURN_NONE;
}


/**
 * @purpose: Write a given buffer to the tracer via ptrace
 * 
 * Converts buffer to words and copies them into tracee's memory at givven addr
 **/
PyObject* write_buffer_to_tracee(pid_t pid, long addr, char *buffer, int length) {   
  const int word_size = sizeof(long);

  union char_word_u {
          long val;
          char chars[word_size];
  } data;

  while (length >= word_size) {
    memcpy(data.chars, buffer, word_size);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_POKEDATA, pid, addr, data.val) == -1);
    length -= word_size;
    buffer += word_size;
    addr += word_size;
  }

  if (length > 0) {
    data.val = ptrace(PTRACE_PEEKTEXT, pid, addr, 0);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(data.val == -1);
    memcpy(data.chars, buffer, length);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_POKEDATA, pid, addr, data.val));
  }

  Py_RETURN_NONE;
}


/**
 * @purpose: Read from tracee
 * 
 **/
PyObject* read_from_tracee(pid_t pid, long addr, char *buffer, int length) {
  const int word_size = sizeof(long);

  union char_word_u {
          long val;
          char chars[word_size];
  } data;

  while (length > 0) {
    data.val = ptrace(PTRACE_PEEKTEXT, pid, addr, 0);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(data.val == -1);
    if (length < word_size) {
      memcpy(buffer, data.chars, length);
    } else {
      memcpy(buffer, data.chars, word_size);
    }
    length -= word_size;
    buffer += word_size;
    addr += word_size;
  }

  Py_RETURN_NONE;
}


static PyObject* py_attach_to_tracee_and_begin(PyObject *self, PyObject *args) {
  pid_t pid;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "i", &pid));
  RETURN_NULL_ON_TRUE(attach_to_tracee_and_begin(pid) == NULL);

  return Py_BuildValue("");
}


static PyObject* py_did_segault(PyObject *self, PyObject *args) {
  pid_t pid;
  siginfo_t siginfo;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "i", &pid));  
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_GETSIGINFO, pid, 0, &siginfo));

  return PyBool_FromLong(siginfo.si_signo == SIGSEGV);
}

static PyObject* py_run_until_enter_or_exit_of_next_syscall(PyObject *self, PyObject *args) {
  pid_t pid;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "i", &pid));

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid, 0, 0) == -1);
  waitpid(pid, 0, 0);

  return Py_BuildValue("");
}


static PyObject* py_get_registers_from_tracee(PyObject *self, PyObject *args) {
  pid_t pid;
  struct user_regs_struct regs;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "i", &pid));
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_GETREGS, pid, 0, &regs) == -1);

  return Py_BuildValue(
      "(KKKKKKKKKKKKKKKKKKKKK)", regs.r15, regs.r14, regs.r13, regs.r12, regs.rbp, 
      regs.rbx, regs.r11, regs.r10, regs.r9, regs.r8, regs.rax, regs.rcx, regs.rdx, regs.rsi,
      regs.rdi, regs.orig_rax, regs.rip, regs.cs, regs.eflags, regs.rsp, regs.ss);
}


static PyObject* py_set_registers_in_tracee(PyObject *self, PyObject *args) {
  pid_t pid;
  struct user_regs_struct regs;

  // TODO: do this less hacky... Right now we don't pass along all registers either way (to python and back), so we need to first get the registers from the tracee, 
  // and then only set the relevant registers. 
  // A probable solution is to always pass all registers back and forth 
  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iKKKKKKKKKKKKKKKKKKKKK", &pid, &regs.r15, &regs.r14, &regs.r13, &regs.r12, &regs.rbp, &regs.rbx, &regs.r11, &regs.r10, &regs.r9, &regs.r8, 
  &regs.rax, &regs.rcx, &regs.rdx, 
  &regs.rsi, &regs.rdi, &regs.orig_rax, &regs.rip, &regs.cs, &regs.eflags, &regs.rsp, &regs.ss));
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_GETREGS, pid, 0, &regs) == -1);
  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iKKKKKKKKKKKKKKKKKKKKK", &pid, &regs.r15, &regs.r14, &regs.r13, &regs.r12, &regs.rbp, &regs.rbx, &regs.r11, &regs.r10, 
  &regs.r9, &regs.r8, &regs.rax, &regs.rcx, &regs.rdx, &regs.rsi, &regs.rdi, &regs.orig_rax, &regs.rip, &regs.cs, &regs.eflags, &regs.rsp, &regs.ss));
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SETREGS, pid, 0, &regs) == -1);

  return Py_BuildValue("");
}


static PyObject* py_write_to_tracee(PyObject *self, PyObject *args) {
  pid_t pid;
  unsigned long long address;
  char *buffer;
  long length;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iKs#", &pid, &address, &buffer, &length));
  RETURN_NULL_ON_TRUE(write_buffer_to_tracee(pid, address, buffer, length) == NULL);

  return Py_BuildValue("");
}


static PyObject* py_read_from_tracee(PyObject *self, PyObject *args) {
  pid_t pid;
  unsigned long long address;
  int length;
  char *buffer;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iKi", &pid, &address, &length));
  buffer = malloc(length);
  RETURN_NULL_ON_TRUE(read_from_tracee(pid, address, buffer, length) == NULL);

  return Py_BuildValue("y#", buffer, length);
}

static PyMethodDef methods[]= {
  {"attach_to_tracee_and_begin", py_attach_to_tracee_and_begin, METH_VARARGS, "Attach to a process and begin execution"},
  {"did_segfault", py_did_segault, METH_VARARGS, "Checks whether the process segfaultes"},
  {"run_until_enter_or_exit_of_next_syscall", py_run_until_enter_or_exit_of_next_syscall, METH_VARARGS, "Continue running tracee until an entering/exiting of syscall"},
  {"get_registers_from_tracee", py_get_registers_from_tracee, METH_VARARGS, "Get the current registers from the tracee"},
  {"set_registers_in_tracee", py_set_registers_in_tracee, METH_VARARGS, "Set the current registers in the tracee"},
  {"write_to_tracee", py_write_to_tracee, METH_VARARGS, "Write memory to tracee"},
  {"read_from_tracee", py_read_from_tracee, METH_VARARGS, "Read memory from tracee"},
	{NULL, NULL, 0, 0}
}; 


static struct PyModuleDef creplayerModule = {
	PyModuleDef_HEAD_INIT,
	"creplayer",
	"description",
	-1,
	methods
};

PyMODINIT_FUNC PyInit_creplayer(void) {
	module = PyModule_Create(&creplayerModule);
  PyModule_AddStringConstant(module, "version", "1.0.0");
	return module;
}

