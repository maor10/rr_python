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
 * Callback for handling sys calls
 **/
PyObject *syscall_handler = NULL;


/** 
 * Callback to determine whether sys call is supported
 **/
PyObject *is_supported_callback = NULL;


/** 
 * Callback to verify ran sys call result
 **/
PyObject *ran_syscall_validator = NULL;


/** 
 * Callback to get registers
 **/
PyObject *get_registers_values_callback = NULL;


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
PyObject* simulate_syscall(int current_syscall_index, struct user_regs_struct regs) {
  PyObject *syscall_result_obj = NULL;
  PyObject *syscall_arg_list = NULL;
  int syscall = regs.orig_rax;
  long syscall_result;

  LOG("Running invalid syscall...");

  regs.orig_rax = -5;
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SETREGS, pid_to_ptrace, 0, &regs) == -1);

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
  waitpid(pid_to_ptrace, 0, WUNTRACED);
  
  LOG("Simulating real sys call...");

  syscall_arg_list = Py_BuildValue(
    "(iKKKKKKKKKKKKKKKKK)", current_syscall_index, syscall, regs.rax, regs.rbx, regs.rcx, regs.rdx, 
  regs.rbp, regs.rsp, regs.rsi, regs.rdi, regs.r8, regs.r9, regs.r10, regs.r11, regs.r12, regs.r13, regs.r14, regs.r15);
  syscall_result_obj = PyObject_CallObject(syscall_handler, syscall_arg_list);
  Py_DECREF(syscall_arg_list);

  RETURN_NULL_ON_TRUE(syscall_result_obj == NULL);
  syscall_result = PyLong_AsLong(syscall_result_obj);
  Py_XDECREF(syscall_result_obj);
  
  regs.rax = syscall_result;
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
  
  Py_RETURN_NONE;
}


/**
 * @purpose: Replay execution of a program, simulating all known sys calls 
 **/

PyObject* replay() {
  struct user_regs_struct regs;
  siginfo_t siginfo;
  int exit_code;
  PyObject *is_supported_result_obj;
  PyObject *register_values_obj;
  int current_syscall_index = 0;

  
  LOG("Replaying...");
  RETURN_NULL_ON_TRUE(attach_to_tracee_and_begin() == NULL);
  LOG("Beginning to run sys call loop...");

  for (;;) {
    if (ptrace(PTRACE_GETSIGINFO, pid_to_ptrace, 0, &siginfo) == -1 && errno == ESRCH) {
      return Py_BuildValue("i", WEXITSTATUS(exit_code));
    }
    RAISE_EXCEPTION_ON_TRUE(siginfo.si_signo == SIGSEGV, "Tracee segfaulted");
    


    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
    waitpid(pid_to_ptrace, 0, 0);

    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_GETREGS, pid_to_ptrace, 0, &regs) == -1);

    LOG("received syscall %lld", regs.orig_rax);
    

    register_values_obj = PyObject_CallFunction(get_registers_values_callback,
      "(iKKKKKKKKKKKKKKKKK)", current_syscall_index, regs.orig_rax, regs.rax, regs.rbx, regs.rcx, regs.rdx, 
      regs.rbp, regs.rsp, regs.rsi, regs.rdi, regs.r8, regs.r9, regs.r10, regs.r11, regs.r12, regs.r13, regs.r14, regs.r15);
    RETURN_NULL_ON_TRUE(NULL == register_values_obj);
    RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(register_values_obj, "KKKKKKKKKKKKKKKK", &regs.rax, &regs.rbx, &regs.rcx, &regs.rdx, 
        &regs.rbp, &regs.rsp, &regs.rsi, &regs.rdi, &regs.r8, &regs.r9, &regs.r10, &regs.r11, &regs.r12, &regs.r13, &regs.r14, &regs.r15));

    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SETREGS, pid_to_ptrace, 0, &regs) == -1);

    is_supported_result_obj = PyObject_CallFunction(is_supported_callback, "(iKKKKKKKKKKKKKKKKK)", current_syscall_index, regs.orig_rax, 
    regs.rax, regs.rbx, regs.rcx, regs.rdx, 
      regs.rbp, regs.rsp, regs.rsi, regs.rdi, regs.r8, regs.r9, regs.r10, regs.r11, regs.r12, regs.r13, regs.r14, regs.r15);
    RETURN_NULL_ON_TRUE(NULL == is_supported_result_obj);
    Py_DECREF(is_supported_result_obj);

    if (!PyObject_IsTrue(is_supported_result_obj)) {
      RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_SYSCALL, pid_to_ptrace, 0, 0) == -1);
      waitpid(pid_to_ptrace, &exit_code, 0);
      if (ptrace(PTRACE_GETREGS, pid_to_ptrace, 0, &regs) != -1) {
        RETURN_NULL_ON_TRUE(PyObject_CallFunction(ran_syscall_validator, "(iK)", current_syscall_index, regs.rax) == NULL);
      }
    } else {
      RETURN_NULL_ON_TRUE(simulate_syscall(current_syscall_index, regs) == NULL);
    }

    current_syscall_index++;
  }
}


/**
 * @purpose: Write a given buffer to the tracer via ptrace
 * 
 * Converts buffer to words and copies them into tracee's memory at givven addr
 **/
PyObject* write_buffer_to_tracee(long addr, char *buffer, int length) {   
  const int word_size = sizeof(long);

  union char_word_u {
          long val;
          char chars[word_size];
  } data;

  while (length >= word_size) {
    memcpy(data.chars, buffer, word_size);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_POKEDATA, pid_to_ptrace, addr, data.val) == -1);
    length -= word_size;
    buffer += word_size;
    addr += word_size;
  }

  if (length > 0) {
    data.val = ptrace(PTRACE_PEEKTEXT, pid_to_ptrace, addr, 0);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(data.val == -1);
    memcpy(data.chars, buffer, length);
    RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(ptrace(PTRACE_POKEDATA, pid_to_ptrace, addr, data.val));
  }

  Py_RETURN_NONE;
}


PyObject* read_from_tracee(long addr, char *buffer, int length) {
  const int word_size = sizeof(long);

  union char_word_u {
          long val;
          char chars[word_size];
  } data;

  while (length > 0) {
    data.val = ptrace(PTRACE_PEEKTEXT, pid_to_ptrace, addr, 0);
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

static PyObject* start_replay_with_pid_and_handlers(PyObject *self, PyObject *args) {
  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "iOOOO", &pid_to_ptrace, &get_registers_values_callback,
  &is_supported_callback,
  &ran_syscall_validator,
  &syscall_handler));
  RAISE_EXCEPTION_ON_TRUE(!PyCallable_Check(is_supported_callback), "Is supported callback must be callable");
  RAISE_EXCEPTION_ON_TRUE(!PyCallable_Check(syscall_handler), "Handler must be callable");
  RAISE_EXCEPTION_ON_TRUE(!PyCallable_Check(ran_syscall_validator), "Validator must be callable");
  
  LOG("Let's Replaying...");
  return replay();
}

static PyObject* set_memory_in_replayed_process(PyObject *self, PyObject *args) {
  unsigned long long address;
  char *buffer;
  long length;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "Ks#", &address, &buffer, &length));
  RETURN_NULL_ON_TRUE(write_buffer_to_tracee(address, buffer, length) == NULL);

  return Py_BuildValue("");
}


static PyObject* get_memory_from_replayed_process(PyObject *self, PyObject *args) {
  unsigned long long address;
  int length;
  char *buffer;

  RETURN_NULL_ON_TRUE(!PyArg_ParseTuple(args, "Ki", &address, &length));

  buffer = malloc(length);
  RETURN_NULL_ON_TRUE(read_from_tracee(address, buffer, length) == NULL);

  return Py_BuildValue("y#", buffer, length);
}

static PyMethodDef methods[]= {
	{"start_replay_with_pid_and_handlers", (PyCFunction)start_replay_with_pid_and_handlers, METH_VARARGS, "(todo docs)"},
  {"set_memory_in_replayed_process", (PyCFunction)set_memory_in_replayed_process, METH_VARARGS, "(todo docs)"},
  {"get_memory_from_replayed_process", (PyCFunction)get_memory_from_replayed_process, METH_VARARGS, "(todo docs)"},
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

