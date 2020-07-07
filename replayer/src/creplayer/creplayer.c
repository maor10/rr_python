#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <Python.h>

#include "utils.h"
#include <sys/signal.h>


/**
 * Python module
 **/
PyObject *module = NULL;


/** 
 * Callback for handling sys calls
 **/
PyObject *syscall_handler = NULL;


/** 
 * Callback to determine whether sys call is supported
 **/
PyObject *is_supported_callback = NULL;


/**
 * Pid of process to replay
 **/ 
int pid_to_ptrace;


/**
 * @purpose: Simulate a requested sys call with python handler instead of running actual sys call
 * 
 * The entry point to this function is ON ENTRY OF SYS CALL
 * We do this by changing the user's requested sys call to an invalid syscall, continuing execution till exit of sys call,
 * and then simulating the sys call ourselves via a pythonic handler before continuing execution of tracee 
 *
 **/
PyObject* simulate_sys_call(struct user_regs_struct regs) {
  PyObject *syscall_result_obj = NULL;
  PyObject *sys_call_arg_list = NULL;
  int syscall = regs.orig_rax;
  long sys_call_result;

  LOG("Running invalid syscall...");

  regs.orig_rax = -5;
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SETREGS, pid_to_ptrace, 0, &regs) == -1);

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
  waitpid(pid_to_ptrace, 0, WUNTRACED);

  LOG("Simulating real sys call...");

  sys_call_arg_list = Py_BuildValue(
    "(KKKKKKKKKKKKKKKKK)", syscall, regs.rax, regs.rbx, regs.rcx, regs.rdx, 
  regs.rbp, regs.rsp, regs.rsi, regs.rdi, regs.r8, regs.r9, regs.r10, regs.r11, regs.r12, regs.r13, regs.r14, regs.r15);
  syscall_result_obj = PyObject_CallObject(syscall_handler, sys_call_arg_list);
  Py_DECREF(sys_call_arg_list);

  RETURN_NULL_ON_TRUE(syscall_result_obj == NULL);
  sys_call_result = PyLong_AsLong(syscall_result_obj);
  Py_XDECREF(syscall_result_obj);
  
  regs.rax = sys_call_result;
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SETREGS, pid_to_ptrace, 0, &regs) == -1);

  LOG("Finished simulation, continue running...");

  Py_RETURN_NONE; 
}


/**
 * @purpose: Attach to the tracee and begin program execution
 * 
 **/
PyObject* attach_to_tracee_and_begin() {
  LOG("Attaching...");
  
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_ATTACH, pid_to_ptrace, 0, 0) == -1);
  waitpid(pid_to_ptrace, 0, 0);
  
  LOG("Send PTRACE_CONT...");

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_CONT, pid_to_ptrace, 0, 0) == -1);
  waitpid(pid_to_ptrace, 0, 0);
  
  LOG("Beginning to run sys call loop...");

  Py_RETURN_NONE;
}


/**
 * @purpose: Determine whether syscall is supported by replayer or not
 * 
 * This is a wrapper function for the callback supplied by python
 * 
 **/
PyObject* is_syscall_supported(long long int syscall) {
  PyObject *is_supported_arg_list = Py_BuildValue("(K)", syscall);
  PyObject *is_supported_result_obj = PyObject_CallObject(is_supported_callback, is_supported_arg_list);
  Py_DECREF(is_supported_arg_list);
  return is_supported_result_obj;
}


/**
 * @purpose: Replay execution of a program, simulating all known sys calls 
 **/

PyObject* replay() {
  struct user_regs_struct regs;
  siginfo_t siginfo;
  PyObject* is_supported_result_obj;

  RETURN_NULL_ON_TRUE(attach_to_tracee_and_begin() == NULL);
  LOG("Beginning to run sys call loop...");
  for (;;) {
    // If we fail here with No such process, the process exited after the last sys call
    RETURN_PY_NONE_ON_TRUE( ptrace(PTRACE_GETSIGINFO, pid_to_ptrace, 0, &siginfo) == -1 && errno == ESRCH);
    RAISE_EXCEPTION_ON_TRUE(siginfo.si_signo == SIGSEGV, "Tracee segfaulted");
    
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
    waitpid(pid_to_ptrace, 0, 0);

    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_GETREGS, pid_to_ptrace, 0, &regs) == -1);
    
    LOG("received syscall %lld", regs.orig_rax);

    is_supported_result_obj = is_syscall_supported(regs.orig_rax);
    RETURN_NULL_ON_TRUE(is_supported_result_obj == NULL);

    if (!PyObject_IsTrue(is_supported_result_obj)) {
      RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
      waitpid(pid_to_ptrace, 0, WUNTRACED);
      continue;
    }

    RETURN_NULL_ON_TRUE(simulate_sys_call(regs) == NULL);
  }

  Py_RETURN_NONE;
}


/**
 * @purpose: Write a given buffer to the tracer via ptrace
 * 
 * Converts buffer to words and copies them into tracee's memory at givven addr
 **/
void write_buffer_to_tracee(int child, long addr, char *buffer, int length) {   
  const int word_size = sizeof(long);
  int size_to_copy = word_size;
  char *current_address;
  int i;
  int loops_needed;
  int has_leftover;
  int leftover;
  union char_word_u {
          long val;
          char chars[word_size];
  } data;

  leftover = length % word_size; 
  has_leftover = leftover != 0; 
  loops_needed = has_leftover ? (length / word_size) + 1 : length / word_size;
  current_address = buffer;
  for (i = 0; i < loops_needed; i++) {
    if (has_leftover && (i == (loops_needed - 1))) {
      size_to_copy = leftover;
    }
    memcpy(data.chars, current_address, size_to_copy);
    ptrace(PTRACE_POKEDATA, child, addr + i * word_size, data.val);
    current_address += size_to_copy;
  }
}


static PyObject* start_replay_with_pid_and_handlers(PyObject *self, PyObject *args) {
  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iOO", &pid_to_ptrace, &is_supported_callback,
  &syscall_handler));
  
  RAISE_EXCEPTION_ON_TRUE(!PyCallable_Check(is_supported_callback), "Is supported callback must be callable");
  RAISE_EXCEPTION_ON_TRUE(!PyCallable_Check(syscall_handler), "Handler must be callable");
  
  return replay();
}

static PyObject* set_memory_in_replayed_process(PyObject *self, PyObject *args) {
  unsigned long long address;
  char *buffer;
  long length;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "Ks#", &address, &buffer, &length));
  write_buffer_to_tracee(pid_to_ptrace, address, buffer, length);

  return Py_BuildValue("");
} 


static PyMethodDef methods[]= {
	{"start_replay_with_pid_and_handlers", (PyCFunction)start_replay_with_pid_and_handlers, METH_VARARGS, "(todo docs)"},
  {"set_memory_in_replayed_process", (PyCFunction)set_memory_in_replayed_process, METH_VARARGS, "(todo docs)"},
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

